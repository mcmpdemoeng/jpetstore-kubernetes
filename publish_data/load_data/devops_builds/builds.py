from datetime import datetime
from load_data.tokens import tokens
from common_utils.constants import (
    loggers,
    BuildTemplate,
    BRANCH,
    BUILD_ENGINE,
    COMMIT,
    DURATION_TIME,
    RUN_ID,
    BUILD_URL_TEMPLATE,
    BUILD_STATUS,
    SERVICE_NAME,
    HREF,
)

import json, requests, traceback

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def post_build_data(tenant_url, bearer_token):

    try:
        TOKEN_API = "dash/api/build/v1/config/tokens"
        DEVOPS_BUILD_TOKEN = tokens.get_token(tenant_url, bearer_token, TOKEN_API)
        ENDPOINT = BUILD_URL_TEMPLATE.format(tenant_url)

        body = BuildTemplate()

        body.build_id = RUN_ID

        date = datetime.utcnow()

        body.built_at = date.isoformat("T") + "Z"

        body.duration = DURATION_TIME * 1000000000

        body.href = ENDPOINT

        body.branch = BRANCH

        body.commit = COMMIT

        body.build_engine = BUILD_ENGINE

        body.build_status = BUILD_STATUS

        body.service_name = SERVICE_NAME

        body.serviceoverride = True

        headers = {
            "Authorization": "TOKEN " + DEVOPS_BUILD_TOKEN.token,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        payload = body.__dict__

        LOGGER.info(json.dumps(payload))

        response = requests.post(data=json.dumps(payload), url=ENDPOINT, headers=headers)
        LOGGER.info("Code = " + str(response.status_code))

        if response.status_code != 200 and response.status_code != 201:
            LOGGER.error("Error = " + str(response.text))
            return False, str(response.text)

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(str(e))
        return False, str(e)

    return True, None
