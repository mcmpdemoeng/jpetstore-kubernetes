from datetime import datetime
from load_data.tokens import tokens
from common_utils.constants import (
    loggers,
    DeploymentTemplate,
    DURATION_TIME,
    HREF,
    PROVIDER,
    RUN_ID,
    DEPLOYMENT_URL_TEMPLATE,
    DEPLOYMENT_STATUS,
    SERVICE_NAME,
    DEPLOYMENT_RUNNING_APP,
)

import json, requests, traceback

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def post_deployment_data(tenant_url, bearer_token):

    try:

        TOKEN_API = "dash/api/deployments/v1/config/tokens"
        DEVOPS_DEPLOYMENTS_TOKEN = tokens.get_token(tenant_url, bearer_token, TOKEN_API)
        ENDPOINT = DEPLOYMENT_URL_TEMPLATE.format(tenant_url)

        body = DeploymentTemplate()

        body.deploymentid = RUN_ID

        body.duration = DURATION_TIME * 1000000

        date = datetime.utcnow()
        body.creation_date = date.isoformat("T") + "Z"

        body.endpoint_hostname = "DEPLOYMENT_RUNNING_APP"

        body.endpoint_service_id = "RUN_ID"

        body.name = SERVICE_NAME

        body.provider = PROVIDER

        body.providerhref = HREF if HREF != "" else tenant_url

        body.status = DEPLOYMENT_STATUS

        body.service_name = SERVICE_NAME

        body.serviceoverride = True

        headers = {
            "Authorization": "TOKEN " + DEVOPS_DEPLOYMENTS_TOKEN.token,
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
