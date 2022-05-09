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

import requests, json, base64

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

    ENDPOINT = GITHUB_API_SECRESTS_ACTIONS_URL.format(GITHUB_SERVER_API, GITHUB_REPO, devops_name)
    LOGGER.info(ENDPOINT)
    devops_token = str(devops_response.token)
    devops_token_encoded = base64.b64encode(devops_token.encode("utf-8")).decode("utf-8")
    LOGGER.info(devops_token_encoded)

    headers = {
        "Authorization": "token {0}".format(GITHUB_TOKEN),
        "accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

    payload = {"encrypted_value": f"{devops_token_encoded}"}

    response = requests.post(url=ENDPOINT, headers=headers, data=payload)
    LOGGER.info(response.json())
    if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
        LOGGER.error("Error = " + str(response.text))
    else:
        LOGGER.info("Creation succeed")
