import time
import datetime
import requests
import os
from common_utils import *
import uuid
import logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Build")


class Builder:
    def __init__(self,  tecnicalServiceName, buildId=uuid.uuid4().__str__(), buildEngine="Jenkins", commitNumber="606b16c15ea6ade03fe70dc9a88c306a54be7a14", buildUrl="http://13.82.103.214:8080/view/RedThread/job/redthread-petstore-deployment-template/71/console", hostname="13.82.103.214:8080", pullRequestNumber="23", repoUrl="https://github.com/mcmpdemoeng/jpetstore-kubernetes.git", details="" ):

        self.branch = f'release-{time.strftime("%Y.%m.%d")}'
        self.build_engine = buildEngine
        self.build_id = buildId
        self.build_status = None
        self.built_at =  None
        self.commit = os.getenv("COMMIT_NUMBER", commitNumber)
        self.details = details
        self.duration = -1
        self.endpoint_hostname = os.getenv("JENKINS_URL", hostname)
        self.endpoint_technical_service_id = hostname.replace(":","_")
        self.event_type = "push"
        self.pull_request_number = pullRequestNumber
        self.repo_url = repoUrl
        self.technical_service_name = tecnicalServiceName
        self.technical_service_override = True
        self.href = os.getenv("BUILD_URL", buildUrl)


    def post_data_into_tenant(self,  buildToken: str, tenantUrl:str ):
        ##Make sure you sanitize the tenant url as the fist step

        tenantUrl = sanitazeTenantUrl(tenantUrl)
        endpointUrl = f"{tenantUrl}dash/api/build/v3/technical-services/builds"

        payload = self.__dict__

        headers = {
            "Authorization": f"TOKEN {buildToken}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        response, success, errorMessage = make_web_request(url=endpointUrl, payload=payload, headers=headers, requestMethod=requests.post)
        LOGGER.info(
            f"Build publishment status code : {response.status_code}"
        )
        if self.build_status == "failed" and success:
            LOGGER.error(f"""
            Publlished build data succesfully:
            {self.__dict__}
            Exiting with status code 1 due to build failure when it ran
            """)
            exit(1)
        elif self.build_status == "failed" and not success:
            LOGGER.error(f"""
            Fail to publish data:
           {self.__dict__}
            Exiting with status code 1 due to build failure when it ran and fail in data publishment
            """)
            exit(1)
        return success, errorMessage



    def docker_logout():
        """
        This function will return 'None' if completed successfully, otherwise an error string will be return
        """
        os.system( "docker logout" )


    def create_docker_image(self,  imageName="defaultName", dockerFileDirectory=".",   ):

        self.built_at = datetime.datetime.utcnow().isoformat("T") + "Z"
        buildCommand = f"sudo docker build -t {imageName} {dockerFileDirectory}"
        self.details = f"Image -> {imageName}"
        try:
            startTime = datetime.datetime.now()
            returnCode = os.system( buildCommand )

            successFulBuild = returnCode == 0
            if not successFulBuild:
                self.build_status = "failed"
                endTime = datetime.datetime.now()
                self.duration = (endTime - startTime).microseconds * 10000
                return {
                "buildDuration": self.duration,
                "buildStatus" : self.build_status
            }

            endTime = datetime.datetime.now()
            self.build_status = "passed"
            self.duration = (endTime - startTime).microseconds * 1000
            return {
                "buildDuration": self.duration,
                "buildStatus" : self.build_status
            }

        except BaseException as error:
            endTime = datetime.datetime.now()
            LOGGER.error(
                f"Fail to buid image '{imageName}' in path '{dockerFileDirectory}'\nError: {error}"
            )
            self.build_status = "failed"
            self.duration = (endTime - startTime).microseconds * 10000
            return {
                "buildDuration": endTime - startTime,
                "buildStatus" : self.build_status
            }



    def upload_docker_image(self,  fullImangeName ) -> str:
        """
        This function will return 'None' if completed successfully, otherwise an error string will be return
        """

        pushCommand = f"docker push {fullImangeName}"

        try:
            returnCode = os.system(pushCommand)
            successfullyExecuted =  returnCode == 0
            if successfullyExecuted:

                return None
            else:
                return f"Fail to push\nCommand: {pushCommand}"

        except BaseException as error:
            return error


    def login_to_docker(self, dockerUser, dockerPassoword):
        """
        This function will return 'None' if completed successfully, otherwise an error string will be return
        """

        loginCommand = f"sudo docker login -u {dockerUser} -p {dockerPassoword}"

        # loginCommand = loginCommand.split(" ")

        try:
            returnCode = os.system(loginCommand)
            successfullyExecuted = returnCode == 0
            if not successfullyExecuted:
                raise Exception(f"Fail to login to docker\nCommand: {loginCommand}")
            return None
        except BaseException as error:

            LOGGER.info(
                f"Fail to login to docker repository \nError: {error}"
            )
            return error



if __name__ == "__main__":
    buildtest = Builder( buildId="thisisisanid", tecnicalServiceName="test3" )
    buildtest.create_docker_image(
        imageName="test3:latest",
    )
    LOGGER.info(
        buildtest.__dict__
    )
    LOGGER.info(
        buildtest.post_data_into_tenant(tenantUrl="https://mcmp-explore-jamesxavier2-mar16-220316202344.multicloud-ibm.com/", buildToken="")
    )

