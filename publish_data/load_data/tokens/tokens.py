from common_utils.constants import loggers, DevOpsToken, TOKEN_NAME, BROKER

import requests, json

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def get_token(tenant_url, bearer_token, path):

    existing_token = _find_existing_token(tenant_url, bearer_token, path)

    if existing_token is not None:
        return existing_token

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

    return DevOpsToken(response.json())


def _find_existing_token(tenant_url, bearer_token, path):

    democloud_token = None

    TOKENS_ENDPOINT = "{0}{1}".format(tenant_url, path)
    LOGGER.info(TOKENS_ENDPOINT)

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
