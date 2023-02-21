import logging
from random import randint, choice
from datetime import datetime, timedelta
import requests
import uuid
from common_utils import make_web_request, sanitazeTenantUrl


PACKAGES = [ "crypto", "object-path", "serializer", "bind", "logger" ]
SEVERITIES = [ "critical", "high", "low", "medium" ]
LICENSE_STATUS = [ "Allowed", "Denied", "NeedApproval" ]

class Secure:
    def __init__(self):
        self.LOGGER = logging.getLogger("secure")
        self.technical_service_name = "RT_petstore_on_aks_jenkins"
        

    def publish_vulnerability_scan( self, tenantUrl, secureToken ):
        tenantUrl = sanitazeTenantUrl(tenantUrl)
        scans = self.__generate_vulnerability_data()
        date = datetime.utcnow().isoformat("T")+"Z"
        ENDPOINT = f"{tenantUrl}dash/api/dev_secops/v3/technical-services/image-scan?scannedBy=BYOStaticscan&scannedTime={date}"

        payload = {
            "vulnerable_image_scan": scans,
            "technicalserviceoverride": True,
            "technical_service_name": self.technical_service_name,
            "provider_href": "https://github.com"
        }

        headers = {
            "Authorization": f"TOKEN {secureToken}"
        }
        response, success, errorMessage =  make_web_request( requestMethod=requests.post, url=ENDPOINT, headers=headers, payload=payload )
        print(f"vulnerability_scan: {response.status_code}")

        return success

    def __generate_vulnerability_data(self):
        scans = []
        for _ in range(randint(5,10)):

            vulnerability = VulnerabilityTemplate()

            vulnerability.cvss_score = randint(0,4)
            vulnerability.description = "This is a security thead information"
            vulnerability.image_digest = str(uuid.uuid4())
            vulnerability.package_name = choice(PACKAGES)
            vulnerability.package_path = "https://github.com/{0}".format(vulnerability.package_name)
            vulnerability.package_version = "{0}.{1}.{2}".format(randint(0,16),randint(0,16),randint(0,16))
            vulnerability.severity = choice(SEVERITIES)
            vulnerability.url_datasource = "https://democloud/datasourceurl"
            vulnerability.vulnerability_id = str(uuid.uuid4())

            scans.append( vulnerability.__dict__ )

        return scans

    def publish_secure_licenses(self, tenant_url, secureToken  ):

        LOGGER = self.LOGGER

        try:

            date = datetime.utcnow().isoformat("T")+"Z"

            ENDPOINT = f"{tenant_url}dash/api/dev_secops/v3/technical-services/license-scan?scannedBy=anchore&scannedTime={date}"
            scan = {"dependency_licenses": []}

            for _ in range(randint(5,10)):

                license = DependencyLicenseTemplate()

                license.dependency_name = choice(PACKAGES)
                license.dependency_version = "v{0}.{1}.{2}".format(randint(0,16),randint(0,16),randint(0,16))
                license.dependency_homepage = "https://www.github.com/{0}".format(license.dependency_name)
                license.dependency_install_path = "/src/node_modules/{0}".format(license.dependency_name)
                license.dependency_package_manager = "node"
                license.license_name = str(uuid.uuid4())
                license.license_link = "https://www.{0}.com/{1}".format(license.dependency_name,str(uuid.uuid4()))
                license.status = choice( LICENSE_STATUS )
                license.provider_href = "https://www.anchore.com"
                license.technical_service_name = self.technical_service_name
                license.technicalserviceoverride = True

                scan["dependency_licenses"].append( license.__dict__ )


            payload = scan
            payload["technical_service_name"] = self.technical_service_name
            payload["technicalserviceoverride"] = True

            headers = { 'Authorization': 'TOKEN ' + secureToken, 'Content-Type': 'application/json', 'accept': 'application/json' }
            
            LOGGER.info( f"Generated dependency_licenses  data: {payload}" )

            response, successfullyPosted, errorMessage = make_web_request(url=ENDPOINT, requestMethod=requests.post, payload=payload, headers=headers, logToIBM=True)
            print(f"secure_licenses: {response.status_code}")
            LOGGER.info( f"response status code: {response.status_code}" )
            

        except Exception as e:
            
            LOGGER.error(str(e))
            return False, str(e)

        return successfullyPosted


class DependencyLicenseTemplate:
    def __init__(self):
        self.dependency_homepage = None
        self.dependency_install_path = None
        self.dependency_name = None
        self.dependency_package_manager = None
        self.dependency_version = None
        self.license_link = None
        self.license_name = None
        self.status = None
        self.provider_href = None
        self.technical_service_name = None
        self.technicalserviceoverride = True

class VulnerabilityTemplate:
    def __init__(self):
        self.cvss_score = 0
        self.description = None
        self.image_digest = None
        self.package_name = None
        self.package_path = None
        self.package_version = None
        self.severity = None
        self.url_datasource = None
        self.vulnerability_id = None



def publishSecureData(tenantUrl, secureToken):
    secure = Secure()
    publishSLSuccessful = secure.publish_secure_licenses(tenantUrl, secureToken)
    publishVSSuccessful = secure.publish_vulnerability_scan(tenantUrl, secureToken)
    if publishSLSuccessful and publishVSSuccessful:
        return True
    return False

if __name__ == "__main__":
    secure =Secure()
    print(
        secure.post_secure_licenses(
            tenant_url="https://mcmp-learn.multicloud-ibm.com",
            secureToken="xBY-7RXdXRM0ZY3dNg4oMz8WMAQKBBbIf1vE_iLFYDW2tJMM43N0i1aKK4iVX4bQ"
        )
    )