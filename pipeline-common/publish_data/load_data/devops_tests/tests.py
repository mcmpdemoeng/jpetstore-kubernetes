from load_data.tokens import tokens
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common_utils.constants import (
    loggers,
    TEST_ENGINE,
    TEST_ENVIRONMENT,
    TEST_FILE,
    TEST_FILE_TYPE,
    TEST_RELEASE,
    TEST_URL_TEMPLATE,
    TEST_TYPE,
    SERVICE_NAME,
    RUN_ID,
    TEST_HREF,
    TEST_TOKEN,
)

import requests, traceback

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


def post_tests_data(tenant_url, bearer_token):

    try:

        TOKEN_API = "dash/api/test/v3/config/tokens"
        DEVOPS_TEST_TOKEN = (
            TEST_TOKEN if TEST_TOKEN != "" else tokens.get_token("TEST", tenant_url, bearer_token, TOKEN_API).token
        )

        ENDPOINT = TEST_URL_TEMPLATE.format(tenant_url, TEST_TYPE, RUN_ID)

        params = (
            ("technicalServiceName", SERVICE_NAME),
            ("fileType", TEST_FILE_TYPE),
            ("testEngine", TEST_ENGINE),
            ("environmentname", TEST_ENVIRONMENT if TEST_ENVIRONMENT != "" else SERVICE_NAME),
            ("releasename", TEST_RELEASE if TEST_RELEASE != "" else SERVICE_NAME)
        )

        m = MultipartEncoder(
            fields={
                "uploadfile": (
                    TEST_FILE,
                    open(
                        TEST_FILE,
                        "rb",
                    ),
                )
            }
        )

        headers = {
            "Authorization": "TOKEN " + DEVOPS_TEST_TOKEN,
            "Content-Type": m.content_type,
            "accept": "application/json",
        }

        LOGGER.info(params, m.fields)

        response = requests.post(url=ENDPOINT, headers=headers, data=m, params=params)

        LOGGER.info("Code = " + str(response.status_code))

        if response.status_code != 200 and response.status_code != 201:
            LOGGER.error("Error = " + str(response.text))
            return False, str(response.text)

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(str(e))
        return False, str(e)

    return True, None
