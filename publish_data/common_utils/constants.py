import os
from common_utils import loggers

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")


class DevOpsToken:
    def __init__(self, other=None):
        self.ID = None
        self.created_by = None
        self.name = None
        self.created_at = None
        self.token = None
        self.broker = None
        self.single_use = None
        self.last_used = None

        if other is not None:
            self.ID = other["ID"]
            self.created_by = other["created_by"]
            self.name = other["name"]
            self.created_at = other["created_at"]
            self.token = other["token"]
            self.broker = other["broker"]
            self.single_use = other["single_use"]
            self.last_used = other["last_used"]


class BuildTemplate:
    def __init__(self):
        self.build_id = None
        self.href = None
        self.built_at = None
        self.duration = -1
        self.href = None
        self.branch = None
        self.commit = None
        self.build_engine = None
        self.build_status = None
        self.service_name = None
        self.serviceoverride = True


class TestTemplate:
    def __init__(self):
        self.duration = -1
        self.failed = -1
        self.passed = -1
        self.status = None
        self.test_type = None
        self.serviceoverride = True


class DeploymentTemplate:
    def __init__(self):
        self.creation_date = None
        self.deploymentid = None
        self.duration = 100572
        self.endpoint_hostname = None
        self.endpoint_service_id = None
        self.name = None
        self.provider = None
        self.providerhref = None
        self.service_name = None
        self.serviceoverride = True
        self.status = None


TOKEN_NAME = os.getenv("TOKEN_NAME", "tokenapp")
BROKER = "mcmp:devops-intelligence:service"
SERVICE_NAME = os.getenv("SERVICE_NAME", "")

RUN_ID = os.getenv("RUN_ID", "")
BRANCH = os.getenv("BRANCH", "")
REPO = os.getenv("REPO", "")
COMMIT = os.getenv("COMMIT", "")

PROVIDER = os.getenv("PROVIDER", "")

UTC_FORMAT = "%FT%TZ"

# Tokens if they are already created for publish data to DevOps Intelligence

BUILD_TOKEN = os.getenv("BUILD_TOKEN", "")
TEST_TOKEN = os.getenv("TEST_TOKEN", "")
DEPLOY_TOKEN = os.getenv("DEPLOY_TOKEN", "")

"""
{0} tenant url (not api url)
{1} service name without  any '/' char
"""
BUILD_URL_TEMPLATE = "{0}dash/api/build/v1/services/builds"

BUILD_STATUS = "passed" if os.getenv("BUILD_STATUS", "") == "success" else "failed"
BUILD_ENGINE = os.getenv("BUILD_ENGINE", "")
BUILD_DURATION_TIME = int(os.getenv("BUILD_DURATION_TIME", 1))
BUILD_HREF = os.getenv("BUILD_HREF", "")

"""
{0} tenant url (not api url)
{1} run unique id
{2} service name without any '/' char
"""
TEST_URL_TEMPLATE = "{0}dash/api/test/v1/services/tests/{1}/run/{2}"

TEST_TYPE = os.getenv("TEST_TYPE", "unit")
TEST_FILE_TYPE = os.getenv("TEST_FILE_TYPE", "xunit")
TEST_ENGINE = os.getenv("TEST_ENGINE", "XUNIT")
TEST_ENVIRONMENT = os.getenv("TEST_ENVIRONMENT", "")
TEST_RELEASE = os.getenv("TEST_RELEASE", "")
TEST_FILE = os.getenv("TEST_FILE", "")
TEST_HREF = os.getenv("TEST_HREF", "")


"""
{0} tenant url (not api url)
"""
DEPLOYMENT_URL_TEMPLATE = "{0}dash/api/deployments/v3/services/deployments"

DEPLOYMENT_PROVIDERS = ["GoCD", "Travis", "Jenkins", "IBM Cloud", "AWS", "Azure", "Google"]
DEPLOYMENT_STATUS = "deployed" if os.getenv("DEPLOYMENT_STATUS", "") == "success" else "failed"
DEPLOY_DURATION_TIME = int(os.getenv("DEPLOY_DURATION_TIME", 1))
DEPLOYMENT_HOSTNAME = os.getenv("DEPLOYMENT_HOSTNAME", "HOSTNAME")
DEPLOYMENT_SERVICE_ID = os.getenv("DEPLOYMENT_SERVICE_ID", "SERVICE_ID")
DEPLOYMENT_HREF = os.getenv("DEPLOYMENT_HREF", "")


# Github secrets
"""
{0} github url (not api url)
"""
GITHUB_SERVER_API = os.getenv("GITHUB_SERVER", "").replace("github.com", "api.github.com")
GITHUB_API_SECRESTS_ACTIONS_URL = "{GITHUB_SERVER_API}/repos/{0}/actions/{1}"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("REPO")
IS_GITHUB = True if os.getenv("IS_GITHUB").lower() in ["true", "1", "t"] else False
