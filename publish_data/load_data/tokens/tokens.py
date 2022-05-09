from common_utils.constants import (
    loggers,
    DevOpsToken,
    TOKEN_NAME,
    BROKER,
    GITHUB_API_SECRESTS_ACTIONS_URL,
    GITHUB_TOKEN,
    GITHUB_REPO,
    GITHUB_SERVER_API,
    IS_GITHUB,
)
from nacl import encoding, public
from base64 import b64encode

import requests, json


LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def get_token(name, tenant_url, bearer_token, path):

    existing_token = _find_existing_token(tenant_url, bearer_token, path)

    if existing_token is not None:
        devops_response = existing_token
        with open(f"{name}_TOKEN", "w") as f:
            LOGGER.info(f"Creating Token for {name}")
            f.write(devops_response.token)

        if IS_GITHUB:
            _github_token_creation(name, devops_response)

        return devops_response

    NEW_TOKEN_ENDPOINT = "{0}{1}".format(tenant_url, path)
    LOGGER.info(NEW_TOKEN_ENDPOINT)

    headers = {
        "Authorization": "Bearer {0}".format(bearer_token),
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {"attributes": [], "broker": BROKER, "name": TOKEN_NAME}

    response = requests.post(url=NEW_TOKEN_ENDPOINT, data=json.dumps(payload), headers=headers)

    if response.status_code != 200 and response.status_code != 201:
        LOGGER.error(response.text)
        raise Exception("Error when creating a new devops token. Code = " + str(response.status_code))

    devops_response = DevOpsToken(response.json())
    with open(f"{name}_TOKEN", "w") as f:
        LOGGER.info(f"Creating Token for {name}")
        f.write(devops_response.token)

    if IS_GITHUB:
        _github_token_creation(name, devops_response)

    return devops_response


def _find_existing_token(tenant_url, bearer_token, path):

    democloud_token = None

    TOKENS_ENDPOINT = "{0}{1}".format(tenant_url, path)

    headers = {"Authorization": "Bearer {0}".format(bearer_token), "accept": "application/json"}

    response = requests.get(url=TOKENS_ENDPOINT, headers=headers)

    if response.status_code == 200:

        paged_data = response.json()

        if "service_tokens" not in paged_data:
            return democloud_token

        for token_dict in paged_data["service_tokens"]:

            local_token = DevOpsToken(token_dict)

            if local_token.name == TOKEN_NAME:
                LOGGER.info("Democloud token found! ID = " + local_token.ID)
                democloud_token = local_token
                break

    if response.status_code != 200:
        LOGGER.error(response.text)
        raise Exception("Error during democloud token existence check. Code {0}".format(response.status_code))

    return democloud_token


def _github_token_creation(devops_name, devops_response: DevOpsToken):

    LOGGER.info(f"Creating Secret Token for {devops_name}")

    SECRET_NAME = f"{devops_name}_TOKEN"
    devops_token = str(devops_response.token)

    PUBLIC_KEY_ENDPOINT = GITHUB_API_SECRESTS_ACTIONS_URL.format(GITHUB_SERVER_API, GITHUB_REPO, "public-key")
    CREATE_SECRET_ENDPOINT = GITHUB_API_SECRESTS_ACTIONS_URL.format(GITHUB_SERVER_API, GITHUB_REPO, SECRET_NAME)

    headers = {
        "Authorization": "token {0}".format(GITHUB_TOKEN),
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url=PUBLIC_KEY_ENDPOINT, headers=headers)
    if response.status_code != 200:
        LOGGER.error("Error Public Key = " + str(response.text))
        return False

    public_key = response.json()

    devops_token_encrypted = _encrypt(public_key["key"], devops_token)

    github_repo = GITHUB_REPO.split("/")

    payload = {
        "encrypted_value": devops_token_encrypted,
        "owner": github_repo[0],
        "repo": github_repo[1],
        "secret_name": SECRET_NAME,
        "key_id": public_key["key_id"],
    }

    response = requests.put(url=CREATE_SECRET_ENDPOINT, headers=headers, data=json.dumps(payload))
    LOGGER.info(response.json())
    if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
        LOGGER.error("Error Secret Creation = " + str(response.text))
        return False

    LOGGER.info(f"Creation of {SECRET_NAME} succeed")
    return True


def _encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")
