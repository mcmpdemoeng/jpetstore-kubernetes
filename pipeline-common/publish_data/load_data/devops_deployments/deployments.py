from datetime import datetime
from load_data.tokens import tokens
from common_utils.constants import (
    loggers,
    DeploymentTemplate,
    DEPLOY_DURATION_TIME,
    DEPLOYMENT_HOSTNAME,
    DEPLOYMENT_SERVICE_ID,
    DEPLOYMENT_HREF,
    DEPLOYMENT_URL_TEMPLATE,
    DEPLOYMENT_STATUS,
    SERVICE_NAME,
    RUN_ID,
    PROVIDER,
    DEPLOY_TOKEN,
    TOOL
)
import time
import json, requests, traceback
from random import randint

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def post_deployment_data(tenant_url, bearer_token):

    try:

        TOKEN_API = "dash/api/deployments/v4/config/tokens"
        DEVOPS_DEPLOYMENTS_TOKEN = (
            DEPLOY_TOKEN
            if DEPLOY_TOKEN != ""
            else tokens.get_token("DEPLOY", tenant_url, bearer_token, TOKEN_API).token
        )
        ENDPOINT = DEPLOYMENT_URL_TEMPLATE.format(tenant_url)

        body = DeploymentTemplate()

        body.deploymentid = RUN_ID
        body.name = SERVICE_NAME
        body.technical_service_name = SERVICE_NAME
        body.provider = PROVIDER
        body.tool = TOOL
        body.status = DEPLOYMENT_STATUS
        body.duration = DEPLOY_DURATION_TIME * 1000000
        date = datetime.utcnow()
        body.creation_date = date.isoformat("T") + "Z"
        body.providerhref = DEPLOYMENT_HREF if DEPLOYMENT_HREF != "" else tenant_url
        body.technicalserviceoverride = True
        body.endpoint_hostname = DEPLOYMENT_HOSTNAME
        body.endpoint_technical_service_id = DEPLOYMENT_SERVICE_ID
        body.release = f'release-2023-{time.strftime("%w")}'
        body.environment = "production"
        body.isproduction = True
        headers = {
            "Authorization": "TOKEN " + DEVOPS_DEPLOYMENTS_TOKEN,
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
