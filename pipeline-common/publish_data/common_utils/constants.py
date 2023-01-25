import os
import random
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
        self.technical_service_name = None
        self.technical_service_override = True
        self.details = None
        self.event_type = None
        self.pull_request_number = None
        self.repo_url = None


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
        self.endpoint_technical_service_id = None
        self.name = None
        self.provider = None
        self.providerhref = None
        self.technical_service_name = None
        self.technicalserviceoverride = True
        self.status = None
        self.tool = None
        self.release = None
        self.environment = None
        self.isproduction = None

class ImageScanTemplate:
    def __init__(self):
        self.vulnerable_image_scan = []
        self.technicalserviceoverride = None
        self.technical_service_name = None
        self.provider_href = ""

class VulnerabilityTemplate:
    def __init__(self,cvss,description,image_digest,pack_name,pack_path,pack_version,severity,url,id):
        self.cvss_score = cvss
        self.description = description
        self.image_digest = image_digest
        self.package_name = pack_name
        self.package_path = pack_path
        self.package_version = pack_version
        self.severity = severity
        self.url_datasource = url
        self.vulnerability_id = id


TOKEN_NAME = os.getenv("TOKEN_NAME", "tokenapp")
BROKER = "mcmp:devops-intelligence:service"
SERVICE_NAME = os.getenv("SERVICE_NAME", "")

RUN_ID = os.getenv("RUN_ID", "")
BRANCH = os.getenv("BRANCH", "")
REPO = os.getenv("REPO", "")
COMMIT = os.getenv("COMMIT", "")

PROVIDER = os.getenv("PROVIDER", "")

TOOL = os.getenv("TOOL", "Jenkins")

UTC_FORMAT = "%FT%TZ"

# Tokens if they are already created for publish data to DevOps Intelligence

BUILD_TOKEN = os.getenv("BUILD_TOKEN", "")
TEST_TOKEN = os.getenv("TEST_TOKEN", "")
DEPLOY_TOKEN = os.getenv("DEPLOY_TOKEN", "")
SECURE_TOKEN = os.getenv("SECURE_TOKEN","")

VULNERABILITIES_URL_TEMPLATE = "{0}dash/api/dev_secops/v3/technical-services/image-scan?scannedBy={1}&scannedTime={2}"

"""
{0} tenant url (not api url)
{1} service name without  any '/' char
"""
BUILD_URL_TEMPLATE = "{0}dash/api/build/v3/technical-services/builds"

BUILD_STATUS = "passed" if os.getenv("BUILD_STATUS", "") == "success" else "failed"
BUILD_ENGINE = os.getenv("BUILD_ENGINE", "")
BUILD_DURATION_TIME =  random.randint(1,5) if int( os.getenv("BUILD_DURATION_TIME", "1").replace("\n","") ) == 1 else int( os.getenv("BUILD_DURATION_TIME", "1").replace("\n","") )
BUILD_HREF = os.getenv("BUILD_HREF", "")

"""
{0} tenant url (not api url)
{1} run unique id
{2} service name without any '/' char
"""
TEST_URL_TEMPLATE = "{0}dash/api/test/v3/technical-services/tests/{1}/run/{2}"

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
DEPLOYMENT_URL_TEMPLATE = "{0}dash/api/deployments/v4/technical-services/deployments"

DEPLOYMENT_PROVIDERS = ["GoCD", "Travis", "Jenkins", "IBM Cloud", "AWS", "Azure", "Google"]
DEPLOYMENT_STATUS = "deployed" if os.getenv("DEPLOYMENT_STATUS", "") == "success" else "failed"
DEPLOY_DURATION_TIME =  random.randint(1,5) if int( os.getenv("DEPLOY_DURATION_TIME", "1").replace("\n",'') ) == 1 else int( os.getenv("DEPLOY_DURATION_TIME").replace("\n",'') )

DEPLOYMENT_HOSTNAME = os.getenv("DEPLOYMENT_HOSTNAME", "HOSTNAME")
DEPLOYMENT_SERVICE_ID = os.getenv("DEPLOYMENT_SERVICE_ID", "SERVICE_ID")
DEPLOYMENT_HREF = os.getenv("DEPLOYMENT_HREF", "")


# Github secrets
"""
{0} github url (not api url)
"""

GITHUB_API_SECRESTS_ACTIONS_URL = "{0}/repos/{1}/actions/secrets/{2}"


GITHUB_SERVER_API = os.getenv("GITHUB_SERVER", "").replace("github.com", "api.github.com")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")
GITHUB_REPO = os.getenv("REPO")
IS_GITHUB = True if os.getenv("IS_GITHUB", "").lower() in ["true", "1", "t"] else False


PETSTORE_REPO_URL = "https://github.com/mcmpdemoeng/jpetstore-kubernetes"
