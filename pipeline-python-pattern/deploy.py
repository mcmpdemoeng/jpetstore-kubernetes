import requests
import datetime
import subprocess
import base64
import os
import random
import time 
import logging
import uuid

from emp_order_reader import read_petstore_order
from common_utils import *

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Deploy")
class Deploy:

    def __init__(self, deployId=uuid.uuid4().__str__(), technical_service_name="RT_petstore_on_aks_jenkins", duration=100572, name="petstore_deployment", applicaitonUrl="http://jpetstore-web.cd6578cfa15a4488b1b8.eastus.aksapp.io/shop/index.do", provider="Azure", status="fail", environment="production", isProduction=True,deployUrl="http://13.82.103.214:8080/view/RedThread/job/redthread-petstore-deployment-template/71/console" ):

        self.creation_date = datetime.datetime.utcnow().isoformat("T") + "Z"
        self.deploymentid = os.getenv( "BUILD_ID", deployId )
        self.duration = duration
        self.endpoint_hostname = applicaitonUrl
        self.endpoint_technical_service_id = f"{applicaitonUrl}".replace("http://","") #TODO: We can improve this
        self.name = name
        self.provider = provider
        self.providerhref = os.getenv( "BUILD_URL", deployUrl )
        self.technical_service_name = technical_service_name
        self.technicalserviceoverride = True
        self.status = status
        self.tool = "Jenkins"
        self.release = f'release-{time.strftime("%Y.%m.%d")}'
        self.environment = environment
        self.isproduction = isProduction


    def deploy_petstore(self, dockerUser, imageTag, tenantUserID, tenantUserApiKey, tenantApi, orderNumber, namespace="jppetstore", jenkinsHome=".." ):
        """
        If fails return an error (string)
        """

        self.creation_date = datetime.datetime.utcnow().isoformat("T") + "Z"
        tenantApi = sanitazeTenantUrl( tenantApi, "api" )

        petstore_details = read_petstore_order(
            tenantApiUrl=tenantApi,
            tenantUserId=tenantUserID,
            tenantUserApikey=tenantUserApiKey,
            orderNumber=orderNumber,
            createKubeconfigFile=True
        )
        startTime = datetime.datetime.now()
        try:
            self.deploy_petstore_helmchart(
                dockerRepo=dockerUser,
                imageTag=imageTag,
                mysqlUrl=petstore_details["db_url"],
                mysqlUser=petstore_details["db_user"],
                mysqlPassword=petstore_details["db_password"],
                petstoreHost=petstore_details["fqdn"],
                jenkinsHome=jenkinsHome
            )

            self.duration =  ( datetime.datetime.now() - startTime ).microseconds
            self.status = "Deployed"
            return None
        except:
            self.duration =  ( datetime.datetime.now() - startTime ).microseconds
            self.status = "Failed"
            return "Fail to deploy petstore"

    @staticmethod
    def deploy_petstore_helmchart(dockerRepo, imageTag, mysqlUrl, mysqlUser, mysqlPassword, petstoreHost,  jenkinsHome="..", namespace="jppetstore" ):
        ##parameters need to be converted to base64 except jenkins path and dockerUser
        ##ensure kubeconfig exists
        ##jenkins home needs to be repopath/helm/modernpets
        startTime = datetime.datetime.now()

        kubeConfigExists = file_exists("tmp_kube_config")
        if not kubeConfigExists:
            endTime = datetime.datetime.now()
            return {
                "deployStatus": "Failed",
                "deplouDuration": endTime - startTime
            }

        cleanPetstore = f"kubectl delete job jpetstoredb --ignore-not-found -n {namespace} --kubeconfig tmp_kube_config".split(" ")
        result = subprocess.run( cleanPetstore )
        if result.returncode != 0:
            LOGGER.error("Fail to delete petstore job ( deployment step 1 )")
            LOGGER.error(result.stdout)
            LOGGER.error(result.stderr)
            raise Exception(f"fail to execute: {result.args}")

        defineHelmPath = f"helm package --destination {jenkinsHome}/modernpets ../helm/modernpets".split(" ")
        result = subprocess.run( defineHelmPath )
        if result.returncode != 0:
            LOGGER.error(f"Fail to define petstore package location ( deployment step 2 )")
            LOGGER.error(result.stdout)
            LOGGER.error(result.stderr)
            raise Exception( result.args )

        helmUpgradeCommand = f"helm upgrade --install --wait --set image.repository={dockerRepo} --set image.tag={imageTag} --set mysql.url={base64.b64encode(mysqlUrl.encode('utf-8')).decode()} --set mysql.username={base64.b64encode(mysqlUser.encode('utf-8')).decode()} --set mysql.password={base64.b64encode(mysqlPassword.encode('utf-8')).decode()} --set isDBAAS=True --set isLB=False --set httpHost={petstoreHost} --namespace={namespace} --create-namespace {namespace} --kubeconfig tmp_kube_config {jenkinsHome}/modernpets/modernpets-0.1.5.tgz --debug".split(" ")
        result = subprocess.run( helmUpgradeCommand )
        endTime = datetime.datetime.now()
        if result.returncode != 0:
            LOGGER.error(f"Fail to deploy petstore ( deployment step 3 )")
            LOGGER.error(result.stdout)
            LOGGER.error(result.stderr)
            raise Exception( result.args )

        LOGGER.info(
            f"Your application is available at http://jpetstore-web.{petstoreHost}"
        )

        return {
            "deployStatus": "success",
            "deployDuration(microseconds)": (endTime - startTime).microseconds
        }


    def post_data_into_tenant( self, deployToken: str, tenantUrl:str,  ):
        ##Make sure you sanitize the tenant url as the fist step
        endpointUrl = f"{tenantUrl}dash/api/deployments/v4/technical-services/deployments"

        payload = self.__dict__

        headers = {
            "Authorization": f"TOKEN {deployToken}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        response, success, errorMessage = make_web_request(url=endpointUrl, payload=payload, headers=headers, requestMethod=requests.post)

        LOGGER.info(
            f"Deploy publishment status code : {response.status_code}"
        )

        return success, errorMessage



if __name__ == "__main__":

    dep = Deploy()
    dep.deploy_petstore(
        dockerUser="mcmpdemo",
        imageTag="latest",
        tenantUserID="625090e80f8c6927409061d4", #mariobv userid
        tenantUserApiKey="ca10f694-8dd2-596b-a3c1-d3df9c5a27db", #replace this
        tenantApi="https://mcmp-learn-api.multicloud-ibm.com",
        orderNumber="6JKY1AMSY4"
    )
