from datetime import datetime
from load_data.tokens import tokens
from common_utils.constants import (
    loggers,
    BuildTemplate,
    BRANCH,
    BUILD_ENGINE,
    COMMIT,
    BUILD_DURATION_TIME,
    RUN_ID,
    BUILD_URL_TEMPLATE,
    BUILD_STATUS,
    SERVICE_NAME,
    BUILD_HREF,
    BUILD_TOKEN,
    PETSTORE_REPO_URL
)

import json, requests, traceback
from random import randint

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def post_build_data(tenant_url, bearer_token):

    try:
        TOKEN_API = "dash/api/build/v3/config/tokens"
        DEVOPS_BUILD_TOKEN = (
            BUILD_TOKEN if BUILD_TOKEN != "" else tokens.get_token("BUILD", tenant_url, bearer_token, TOKEN_API).token
        )
        ENDPOINT = BUILD_URL_TEMPLATE.format(tenant_url)

        body = BuildTemplate()

        body.branch = BRANCH
        body.build_engine = BUILD_ENGINE
        body.build_id = RUN_ID
        body.build_status = BUILD_STATUS
        date = datetime.utcnow()
        body.built_at = date.isoformat("T") + "Z"
        body.commit = COMMIT
        body.details = "No details"
        body.duration = BUILD_DURATION_TIME * 1000000000
        body.event_type = "push"
        body.pull_request_number = str(randint(10,100))
        body.repo_url = PETSTORE_REPO_URL
        body.technical_service_name = SERVICE_NAME
        body.technical_service_override = True        
        body.href = BUILD_HREF

        headers = {
            "Authorization": "TOKEN " + DEVOPS_BUILD_TOKEN,
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
