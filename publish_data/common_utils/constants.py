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
HREF = os.getenv("HREF", "")

RUN_ID = os.getenv("RUN_ID", "")
BRANCH = os.getenv("BRANCH", "")
REPO = os.getenv("REPO", "")
COMMIT = os.getenv("COMMIT", "")

DURATION_TIME = int(os.getenv("DURATION_TIME", 1))

PROVIDER = os.getenv("PROVIDER", "")

UTC_FORMAT = "%FT%TZ"

"""
{0} tenant url (not api url)
{1} service name without  any '/' char
"""
BUILD_URL_TEMPLATE = "{0}dash/api/build/v1/services/builds"

# ENGINES = ["Jenkins", "Travis", "GitHub Actions"]
# BRANCHES = ["dev", "main", "release"]

# BUILD_STATUS = ["pass", "fail", "passed", "failed"]
BUILD_STATUS = "passed" if os.getenv("BUILD_STATUS", "") == "success" else "failed"
BUILD_ENGINE = os.getenv("BUILD_ENGINE", "")

"""
{0} tenant url (not api url)
{1} run unique id
{2} service name without any '/' char
"""
TEST_URL_TEMPLATE = "{0}dash/api/test/v1/services/tests/{1}/run/{2}"

# TEST_TYPE = ["unit", "function", "scale", "codecoverage"]
TEST_TYPE = os.getenv("TEST_TYPE", "unit")
TEST_FILE_TYPE = os.getenv("TEST_FILE_TYPE", "xunit")
TEST_ENGINE = os.getenv("TEST_ENGINE", "XUNIT")
TEST_ENVIRONMENT = os.getenv("TEST_ENVIRONMENT", "")
TEST_RELEASE = os.getenv("TEST_RELEASE", "")
TEST_FILE = os.getenv("TEST_FILE", "")


"""
{0} tenant url (not api url)
"""
DEPLOYMENT_URL_TEMPLATE = "{0}dash/api/deployments/v3/services/deployments"

# DEPLOYMENT_STATUS = ["Deployed", "Failed"]

DEPLOYMENT_PROVIDERS = ["GoCD", "Travis", "Jenkins", "IBM Cloud", "AWS", "Azure", "Google"]
DEPLOYMENT_RUNNING_APP = "http://democloud-lampstack-website.s3-website.us-east-2.amazonaws.com/"
DEPLOYMENT_STATUS = "deployed" if os.getenv("DEPLOYMENT_STATUS", "") == "success" else "failed"
