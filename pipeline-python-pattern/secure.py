import logging
from random import randint, choice
from datetime import datetime, timedelta
import requests
import uuid
import logging
import hashlib

from common_utils import make_web_request, sanitazeTenantUrl, LICENSES

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("secure")

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

        print(
            response.text
        )
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
            tenant_url = sanitazeTenantUrl(tenant_url)
            ENDPOINT = f"{tenant_url}dash/api/dev_secops/v3/technical-services/license-scan?scannedBy=licenseFinder&scannedTime={date}"
            scan = {"dependency_licenses": []}

            for _ in range(randint(1,2)):

                license = DependencyLicenseTemplate()

                licenseInfo = choice(LICENSES)

                license.dependency_name = licenseInfo["Package Name"]
                license.dependency_version = "v{0}.{1}.{2}".format(randint(0,16),randint(0,16),randint(0,16))
                license.dependency_homepage = "https://www.github.com/{0}".format(license.dependency_name)
                license.dependency_install_path = "/src/node_modules/{0}".format(license.dependency_name)
                license.dependency_package_manager = "node"
                license.license_name = licenseInfo['License Name']
                license.license_link = "https://www.{0}.com/{1}".format(license.dependency_name,str(uuid.uuid4()))
                license.status = choice( LICENSE_STATUS )
                license.provider_href = "https://pypi.org/"
                license.technical_service_name = self.technical_service_name
                license.technicalserviceoverride = True

                scan["dependency_licenses"].append( license.__dict__ )


            payload = scan
            payload["technical_service_name"] = self.technical_service_name
            payload["technicalserviceoverride"] = True

            headers = { 'Authorization': 'TOKEN ' + secureToken, 'Content-Type': 'application/json', 'accept': 'application/json' }
            
            LOGGER.info( f"Generated dependency_licenses  data: {payload}" )

            response, successfullyPosted, errorMessage = make_web_request(url=ENDPOINT, requestMethod=requests.post, payload=payload, headers=headers, logToIBM=True)
            print(
                response.text
            )
            print(f"secure_licenses: {response.status_code}")
            LOGGER.info( f"response status code: {response.status_code}" )
            

        except Exception as e:
            
            LOGGER.error(str(e))
            return False, str(e)

        return successfullyPosted


    def publish_static_scan( self, tenantUrl, secureToken, date=datetime.utcnow().isoformat("T")+"Z", numberOfVulnerabilities=randint(1,4)  ):
        tenantUrl = sanitazeTenantUrl(tenantUrl)
        ENDPOINT = f"{tenantUrl}dash/api/dev_secops/v3/technical-services/static-scan"
        headers = {
            "Authorization": f"Token {secureToken}"
        }

        vulnerabilitiesList = [ self.__generate_static_scan_vulnerability(formatedDate=date) for _ in range(numberOfVulnerabilities) ]
        
        #Add at least one critical for the Static scan dashboard
        vulnerabilitiesList.append( self.__generate_static_scan_vulnerability(severity="CRITICAL", formatedDate=date)) 
        
        payload = {
            "endpoint_hostname": "sampleDatssa.net",
            "provider_href": self.technical_service_name,
            "scanned_time": date,
            "scannedby": "On-premise",
            "technical_service": self.technical_service_name,
            "technical_service_tag": { "additionalProp1": "string" },
            "technicalserviceoverride": True,
            "vulnerabilities": vulnerabilitiesList,
            "vulnerability_density": randint( numberOfVulnerabilities , numberOfVulnerabilities+3 )
        }
        LOGGER.info( f"static scan sample payload: {payload}" )
        response, _, errorMessage = make_web_request( requestMethod=requests.post, url=ENDPOINT, headers=headers, payload=payload )
        LOGGER.info( f"static scan: {response.status_code if response else 'None'}" )
        
        return response.status_code if response else None


    def __generate_static_scan_vulnerability(self, formatedDate=datetime.now().isoformat("T")+"Z", severity=choice([ "CRITICAL", "HIGH", "MEDIUM","CRITICAL" ])):
        startLine =randint(1,455)
        endLine = startLine + randint(3,20)
        description = "This is an autogenerated vulnerability for sample data"
        return {
                "actions": [ "string" ],
                "attr": { "jira-issue-key": "string" },
                "author": "string",
                "closeDate": formatedDate,
                "comments": [
                    {
                    "createdAt": formatedDate,
                    "htmlText": description,
                    "key": "string",
                    "login": "string",
                    "markdown": description,
                    "updatable": True
                    }
                ],
                "component": f"sample_data_component_{str(uuid.uuid4())}",
                "creationDate": formatedDate,
                "debt": "string",
                "effort": choice(["HIGH", "MEDIUM", "LOW"]),
                "hash": "sampledatahash",
                "key": str(uuid.uuid4()),
                "line": startLine,
                "message": description,
                "project": self.technical_service_name,
                "resolution": description,
                "rule": "Default", # TODO: Chage this 
                "severity": severity,
                "status": choice(["OPEN","CONFIRMED","REOPENED"]),
                "tags": [ "string" ],
                "textRange": { "endLine": endLine, "endOffset": endLine, "startLine": startLine, "startOffset": startLine },
                "transitions": ["string"],
                "type": "Critical",
                "updateDate": formatedDate
            }

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


def generate_vulnerability_data( date=datetime.utcnow(), vulnerabilityDaysOfAge=3, vulnerabilitySourceTool=choice(["Docker", "Kubernetes", "Mysql"] )  ):

    vulnerabilityScore = randint(1, 10 )

    severity = get_severityLevel(vulnerabilityScore)

    return {
      "affectedProjectCount": randint(1, 8 ),
      "cvssV2BaseScore": vulnerabilityScore,
      "cvssV2ExploitabilitySubScore": vulnerabilityScore,
      "cvssV2ImpactSubScore": vulnerabilityScore,
      "cvssV2Vector": choice(["vector1", "vector2"]),  ##TODO: put realistic values
      "cvssV3BaseScore": vulnerabilityScore,
      "cvssV3ExploitabilitySubScore": vulnerabilityScore,
      "cvssV3ImpactSubScore": vulnerabilityScore,
      "cvssV3Vector": choice(["vector1", "vector2"]),  ##TODO: put realistic values,
      "dependencies": choice(["None", "sample Dependence"]), ##TODO: put realistic values,
      "description": "This is a sample autogenerated vulnerability",
      "published": (date - timedelta(days=vulnerabilityDaysOfAge)).isoformat("T")+"Z",
      "references": choice(["None", "sample reference"]), ##TODO: put realistic values,
      "riskscore": vulnerabilityScore,
      "severity": severity,
      "sha256": hashlib.sha256(f"ThisIsASamplesha256-{str(uuid.uuid4())}".encode()).hexdigest(),
      "source":  vulnerabilitySourceTool, ##TODO: Make sure this is correct
      "title": f"{vulnerabilitySourceTool} - sev {severity}",
      "updated":  date.isoformat("T")+"Z",
      "url": choice(["https://www.cvedetails.com/cve/CVE-2021-25743/"]), ## TODO: we can provide a kubernetes url for kubernest and docker for doker vulnerabilities
      "uuid": str(uuid.uuid4()),
      "vulnId": str(uuid.uuid4()),
      "weakness": choice(["Web Page", "REST API"])
    }

def get_severityLevel(vulnerabilityScore):

    if vulnerabilityScore >= 3:
        severity = "LOW"
    elif vulnerabilityScore > 3 and vulnerabilityScore < 8:
        severity = "MEDIUM"
    else:
        severity = "CRITICAL"

    return severity
    
def generate_dcheck_payload(date=datetime.utcnow(), daysOfAge=5, technicalService="sample_data"):
    affectedComponent = choice(['Kubernetes Cluster', 'Java', 'Javascript', 'Docker Image' ])
    return {
        "component_license": "Petstore",
        "component_name": affectedComponent,
        "component_uuid": str(uuid.uuid4()),
        "component_version": f"{randint(1,4)}.{randint(5,32)}.{randint(1,9)}",
        "endpoint_hostname": "http://jpetstore-web.cd6578cfa15a4488b1b8.eastus.aksapp.io", 
        "first_occurrence_time": (date - timedelta(days=daysOfAge)).isoformat("T")+"Z",
        "last_occurrence_time": date.isoformat("T")+"Z",
        "policy_violations_license_total": randint(1,3),
        "policy_violations_total": randint(3,6),
        "project_name": "Petstore",
        "project_uuid": "PetstoreApplication",
        "provider_href": "https://github.com",
        "scanned_by": "On-premise",
        "technical_service": technicalService,
        "technical_service_override": True,
        "technical_service_tag": {
            "application": "petstore",
        },
        "vulnerabilities": [ generate_vulnerability_data(vulnerabilitySourceTool=affectedComponent) for _ in range(0, daysOfAge) ]
    }


def publish_sample_dcheck(tenantUrl, secureToken, technicalService="sample_data", date=datetime.utcnow()):

    tenantUrl = sanitazeTenantUrl(tenantUrl)
    ENDPOINT = f"{tenantUrl}dash/api/dev_secops/v3/technical-services/dependency-check"

    headers = {
        "Authorization": f"Token {secureToken}"
    }

    payload = generate_dcheck_payload(date=date, technicalService=technicalService)
    LOGGER.info( f"dtrack sample payload: {payload}" )

    response, _, errrorMessage = make_web_request( url=ENDPOINT, requestMethod=requests.post, headers=headers, payload=payload, logToIBM=False )

    LOGGER.info(f"post_sample_dcheck: {response.status_code if response else 'None'}")

    return response.status_code if response else None







def publishSecureData(tenantUrl, secureToken):
    secure = Secure()
    publishSL = secure.publish_secure_licenses(tenantUrl, secureToken)
    publishVS = secure.publish_vulnerability_scan(tenantUrl, secureToken,)
    publishSS = secure.publish_static_scan( tenantUrl, secureToken,  )
    publishDT = publish_sample_dcheck(tenantUrl, secureToken, technicalService=secure.technical_service_name)

    if publishSL and publishVS and publishSS and publishDT:
        return True
    return False

if __name__ == "__main__":
    secure =Secure()
    # print(
    #     secure.publish_vulnerability_scan(
    #         tenantUrl="https://mcmp-learn.multicloud-ibm.com",
    #         secureToken="xBY-7RXdXRM0ZY3dNg4oMz8WMAQKBBbIf1vE_iLFYDW2tJMM43N0i1aKK4iVX4bQ"
    #     )
    # )
    print(
        secure.publish_secure_licenses(
            tenant_url="https://mcmp-learn.multicloud-ibm.com",
            secureToken="xBY-7RXdXRM0ZY3dNg4oMz8WMAQKBBbIf1vE_iLFYDW2tJMM43N0i1aKK4iVX4bQ"
        )
    )