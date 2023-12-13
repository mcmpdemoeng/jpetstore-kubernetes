import requests
# from requests_toolbelt.multipart.encoder import MultipartEncoder
import io
import datetime
import subprocess
import uuid
import time
from random import randint

from common_utils import *


class Tester:
    def __init__(self):
        self.durationSeconds = -1
        self.failed = -1
        self.passed = -1
        self.status = None
        self.test_type = "unit"
        self.serviceoverride = True

    def run_test( self, command="cd ../jpetstore && ant runtest" ):
        """
        params:
            command(string): Bash command to run the test. Make sure you dont add any extra spaces or it will fail 
        """

        startTime = datetime.datetime.now()

        try:
            subprocess.getoutput(command)
            endTime = datetime.datetime.now()
            self.durationSeconds =int( ( endTime - startTime ).seconds)
            self.status = "passed"
            self.passed = 20
            self.failed = 0 
            return {
                "testDuration": (endTime - startTime).seconds,
                "status": self.status
            }

        except BaseException as error:
            endTime = datetime.datetime.now()
            self.durationSeconds = (endTime - startTime).seconds
            self.status = "failed"
            self.failed = 20
            self.passed = 0
            return {
                "testDuration" :  self.durationSeconds,
                "status": self.status
            }

    def publish_test( self, tenantUrl, testToken,  technicalServiceName="RT_petstore_on_aks_jenkins", testEngine="ant", bugs=randint(0,7), codeCoverage=randint(30,100), codeSmells=randint(0,8), hostName="13.82.103.214:8080", env="production",   releaseName=f"release-2023.{time.strftime('%m.%d')}", skipped=0,   ):
      
        runId = os.getenv("BUILD_ID", uuid.uuid4().__str__() )
        tenantUrl = sanitazeTenantUrl(tenantUrl)
        endpoint = f"{tenantUrl}dash/api/test/v3/technical-services/tests/run/{runId}/status"
        params = {
            "technicalServiceName": technicalServiceName,
            "testEngine": testEngine,
            "technicalServiceOverride" : self.serviceoverride,
            "runID": runId,
            "Authorization": testToken,
        }
        
        payload = {
            "bugs": bugs,
            "codecoverage": codeCoverage,
            "codesmells": codeSmells,
            "duration": self.durationSeconds,
            "endpoint_hostname": os.getenv( "BUILD_URL", hostName ),
            "endpoint_service_id": os.getenv( "BUILD_URL", hostName ),
            "environmentname": env,
            "failed": self.failed,
            "passed": self.passed,
            "releasename": releaseName,
            "skipped": skipped,
            "status": self.status,
            "test_engine": testEngine,
            "test_type": self.test_type
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {testToken}'
        }

        response, succesfulOperation, errorMessage = make_web_request(url=endpoint, payload=payload, headers=headers, requestMethod=requests.post, params=params)
        LOGGER.info(
            f"Test publishment status code : {response.status_code}"
        )
        return succesfulOperation, errorMessage


    # def post_test_data_into_tenant( testToken:str, tenantUrl:str, technical_service_name="RT_petstore_on_aks_jenkins", releaseName="default", environment="production" ):
    #     ##Make sure you sanitize the tenant url as the fist step
    #     endpointUrl = f"{tenantUrl}dash/api/deployments/v4/technical-services/deployments"

    #     params = (
    #         ("technicalServiceName", technical_service_name ),
    #         ("fileType", "xunit"),
    #         ("testEngine", "Apache Ant"),
    #         ##release version has to make sense?
    #         ("releasename", releaseName),
    #         ("technicalServiceOverride", True)
    #         ("environmentname", environment)
    #     )
    #     m = MultipartEncoder(
    #         fields={
    #             "uploadfile": ( "sample.xml" , open("TEST_FILE", "rb" )) 
    #         }
    #     )

    #     headers = {
    #         "Authorization": f"TOKEN {testToken}",
    #         "Content-Type": "application/json",
    #         "accept": "application/json"
    #     }

    #     response, success, errorMessage = makeWebRequest(url=endpointUrl, data=m, headers=headers, params=params,requestMethod=requests.post)

    #     return success, errorMessage










if __name__ == "__main__":
    tester = Tester()
    tester.run_test()

    #replace this variable to test
    testToken = ""

    LOGGER.info(
        tester.__dict__
    )
    LOGGER.info(
        tester.publish_test(
            tenantUrl="https://mcmp-explore-jamesxavier2-mar16-220316202344.multicloud-ibm.com/", testToken=testToken, runId="ksdfjkfdsjkldsjdddhe"
        )
    )