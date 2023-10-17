import argparse
import os
import json
import logging
import requests
import build
from datetime import datetime
import uuid
import logging

from secure import Secure
import deployMonitoring
import build
from testpetstore import Tester
from deploy import Deploy
from common_utils import *

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Pipeline")

STATE_FILENAME = "jpetstore-pipeline-status.json"

def parser( validate_parameters = False ) -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument("-gt", "--github-token", help="<Optional> Github Token")
    parser.add_argument( '-du', "--docker-user", help='<Required> Docker username to access docker hub', required=True )
    parser.add_argument( '-dp', "--docker-password", help='<Required> Docker password to access docker hub', required=True )
    parser.add_argument( '-tn', "--tenant-url",  help='<Required> Tenant url  in the following format: "https://mcmp-explore-example.multicloud-ibm.com/"  ', required=True )
    parser.add_argument( '-uid', "--user-id",  help='<Required> User ID of the tenant"  ', required=True )
    parser.add_argument( '-ukey', "--user-api-key",  help='<Required> User api key of the tenant"  ', required=True )
    parser.add_argument( '-bt', "--build-token",  help='<Required> DevOps intellingence build token"  ', required=True )
    parser.add_argument( '-tt', "--test-token",  help='<Required> DevOps intellingence test token"  ', required=True )
    parser.add_argument( '-dt', "--deploy-token",  help='<Required> DevOps intellingence deploy token"  ', required=True )
    parser.add_argument( '-st', "--secure-token",  help='<Required> DevOps intellingence secure token"  ', required=True )
    parser.add_argument( '-on', "--order-number",  help='<Required> Order number of the petstore infrastructure provisined"  ', required=False, default="" ) #can be optional for the changes triggered from github
    parser.add_argument( '-ff', "--fulfillment-id",  help='<Required> Fulfillment id of the petstore infrastructure provisined"  ', required=False, default="" ) #can be optional for the changes triggered from github

    values = parser.parse_args()
    if validate_parameters:
        validate_parameters(values.__dict__)

    return values.__dict__

def validate_parameters(parameters: dict) -> dict:
    return {}


def main():
    parserValues = parser()
    pipelineParams = configure_pipeline_status( parserValues )
    LOGGER.info( json.dumps( pipelineParams, indent=3 ) )
    buildUrl =  os.getenv( "BUILD_URL", "http://13.82.103.214:8080/view/RedThread/job/redthread-petstore-deployment-template/71/console" )

    tenantUrl = sanitazeTenantUrl(pipelineParams['tenant_url'])

    error = update_completed_order_status( 
        tenantUrl=tenantUrl, 
        userID=pipelineParams['user_id'], 
        userApiKey=pipelineParams['user_api_key'], 
        orderNumber=pipelineParams["order_number"],   
        fulfillmentId=pipelineParams["fulfillment_id"],
        buildUrl=buildUrl
    )
    if error:
        LOGGER.error("Fail to update order status")

    petstore_pipeline(params=pipelineParams)






def update_completed_order_status( tenantUrl:str, userID:str, userApiKey:str, orderNumber: str, fulfillmentId:str, buildUrl:str ):
    """
    This function will return an error string only in case of failure
    """
    ##If status file is not json valid create a new one and rename the existing one to .old

    tenantUrl = sanitazeTenantUrl(tenantUrl, urlType='api')
    endpointUrl = f"{tenantUrl}api/fulfillment/prov_posthook_response"
    headers = {
        "username": userID,
        "apikey": userApiKey
    }

    payload = {
        "additionalMessage":f"Provisioning Completed. Check build {buildUrl} console",
        "comments":"Provisioned Completed.",
        "orderNumber": orderNumber,
        "serviceFulfillmentId": fulfillmentId,
        "status":"ProvisionCompleted",
        "version":""
    }

    response, operationSuccess, errorMessage = make_web_request( url=endpointUrl, headers=headers, payload=payload, requestMethod=requests.post )
    if not operationSuccess:
        return f'Unable to update order status "{orderNumber}, with the credentials provided"\nError: "{errorMessage}"' 
    
    return None



def petstore_pipeline(  params: dict  ):

    fullWebImageName = f"{params['docker_user']}/jpetstore-web:latest"
    fullDBImageName = f"{params['docker_user']}/jpetstore-db:latest"
    technicalServiceName = "RT_petstore_on_aks_jenkins"
 
    LOGGER.info("Building pestore web image")
    result = build_petstore( 
        dockerFileDirectory="../jpetstore",
        dockerUser=params['docker_user'], 
        dockerPassword=params['docker_password'], 
        fullImageName=fullWebImageName, 
        tenantUrl=params['tenant_url'], 
        buildToken=params['build_token'], 
        publishToTenant=True,
        pushToDockerRepo=True,
        technicalServiceName=technicalServiceName
        )

    LOGGER.info("Building pestore db image")
    result = build_petstore( 
        dockerFileDirectory="../",
        dockerUser=params['docker_user'], 
        dockerPassword=params['docker_password'], 
        fullImageName=fullDBImageName,
        tenantUrl=params['tenant_url'],
        buildToken=params['build_token'],
        publishToTenant=True,
        pushToDockerRepo=True,
        technicalServiceName=technicalServiceName
        )
    LOGGER.info("testing pestore")

    result = test_petstore( 
        tenantUrl=params["tenant_url"], 
        testToken=params["test_token"], 
        technicalServiceName=technicalServiceName 
    )
    
    tenantApiUrl = sanitazeTenantUrl(tenantUrl=params["tenant_url"], urlType="api")
    LOGGER.info("deploying pestore")
    result = deploy_Petstore( 
        dockerUser=params["docker_user"],
        imageTag="latest",
        tenantUserID=params["user_id"],
        tenantUserApiKey=params["user_api_key"],
        tenantApiURL=tenantApiUrl,
        orderNumber=params["order_number"],
        deployToken=params["deploy_token"],
        publishToTenant=True
     )

    secure_Petstore(tenantUrl=params["tenant_url"], secureToken=params["secure_token"])
    successfulOperation = deployMonitoring.deploy_petstore_monitoring()
    if not successfulOperation:
        LOGGER.error("Unable to install monitoring")


def configure_pipeline_status( newValues: dict ):

    #TODO we can apply the same logic of the order number here to any missing parameter so that the file state can wor as a backup

    #verify if the file already exists
    if not os.path.exists( STATE_FILENAME ):
        LOGGER.info(f"{STATE_FILENAME} doesnt exist, creating it...")
        write_to_file( STATE_FILENAME, json.dumps(newValues) )
        return newValues
    
    
    LOGGER.info("State file already exists, comparing parameters")

    fileContent = read_state_file( STATE_FILENAME )
    LOGGER.info(f"File state content ({STATE_FILENAME}):")
    LOGGER.info(fileContent)
    dictFileContent = json.loads( fileContent )

    orderIsempty = newValues['order_number'] == ""
    fulfillmentIsEmpty = newValues['fulfillment_id'] == ""

    if orderIsempty:
        LOGGER.info("Order is number is empty, reading order_nubmer and fulfillment_id values from state file")
        newValues["order_number"] = dictFileContent['order_number']
        newValues["fulfillment_id"] = dictFileContent["fulfillment_id"]

        return newValues

    elif not orderIsempty and not fulfillmentIsEmpty :
        #if  order number and fulfillment id overwrite the file
        LOGGER.info(f"updating {STATE_FILENAME} " )
        write_to_file( STATE_FILENAME, json.dumps(newValues) )
        LOGGER.info("DONE")
        return newValues         
    
    
    else:
        LOGGER.error("To use a new petstore infrasturcture you are required to send the fulfillment_id and order_number, otherwise the old values from state file will be used")
        LOGGER.warning("Using the old values from the state file")
        return dictFileContent
    #if this fails return the values and show a warning that we are not saving the status 
    #if posible write a log


def write_to_file( fileName:str, content:str ) -> str:
    try:
        file = open( fileName, "w+" )
        file.write(content)
        file.close()
        return None

    except BaseException as error:
        LOGGER.error(f"Fail to write {STATE_FILENAME}, \nError: {error}  ")
        return error

def read_state_file(fileName: str):
    #TODO verify the file is json valid

    try:
        file = open(STATE_FILENAME, 'r')
        fileContent = file.read()
        file.close()
        
        return fileContent

    except BaseException as error:
        LOGGER.error(  f"Fail to read file {STATE_FILENAME}, \n if this error persists delete the file and send all parameters to the pipeline"  )
        raise Exception(f"Unable to read '{STATE_FILENAME}'\nError: {error} ")

def build_petstore( dockerFileDirectory=".", dockerUser="", dockerPassword="", fullImageName="", tenantUrl="", buildToken="", publishToTenant=False, pushToDockerRepo=False, technicalServiceName="RT_petstore_on_aks_jenkins" ):

    petstoreBuild = build.Builder( buildId=uuid.uuid4().__str__(), tecnicalServiceName=technicalServiceName )
    startTime = datetime.now()
    petstoreBuild.create_docker_image( dockerFileDirectory=dockerFileDirectory, imageName=fullImageName )
    
    if pushToDockerRepo:
        if not dockerUser or not dockerPassword:
            raise Exception("Error:build_petstore: dockerUser and dockerPassword are required for publishment")
        petstoreBuild.login_to_docker( dockerUser=dockerUser, dockerPassoword=dockerPassword )
        petstoreBuild.upload_docker_image( fullImageName )
    if publishToTenant:
        if not tenantUrl or not buildToken:
            raise Exception("Error:build_petstore: tenantUrl and buildToken are required for publishment")
        tenantUrl = sanitazeTenantUrl( tenantUrl )
        petstoreBuild.post_data_into_tenant(buildToken=buildToken, tenantUrl=tenantUrl)

    duration =   datetime.now() - startTime
    SecondsDuration = duration.total_seconds()
    if petstoreBuild.build_status == "failed":
        LOGGER.error(f"Fail to build {fullImageName}")
        exit(1)

def test_petstore( tenantUrl, testToken, technicalServiceName ):
    tester = Tester()
    tester.run_test()
    try:
        tester.publish_test(
            tenantUrl=tenantUrl,
            testToken=testToken,
            technicalServiceName=technicalServiceName
        )
    except:
        LOGGER.error("Error: Fail to publish test data")
        LOGGER.info(tester.__dict__)

    
def deploy_Petstore( tenantUserID,  tenantUserApiKey, tenantApiURL,  orderNumber, deployToken="", imageTag="latest", dockerUser="mcmpdemo",publishToTenant=False ):
    deployment = Deploy()
    deployment.deploy_petstore (
        dockerUser=dockerUser,
        imageTag=imageTag,
        tenantUserID=tenantUserID,
        tenantUserApiKey=tenantUserApiKey,
        tenantApi=tenantApiURL,
        orderNumber=orderNumber
    )
    tenantUrl = sanitazeTenantUrl(tenantApiURL)

    if publishToTenant:
        if not deployToken:
            raise Exception("deploy_Petstore: deployToken needed to publish data to tenant")
        deployment.post_data_into_tenant( tenantUrl=tenantUrl, deployToken=deployToken )

    if deployment.status.lower() == "failure":
        exit(1)

def secure_Petstore( tenantUrl, secureToken ):
    secure = Secure()
    publishSLSuccessful = secure.publish_secure_licenses( tenantUrl, secureToken )
    publishVSSuccessful = secure.publish_vulnerability_scan( tenantUrl, secureToken )
    if publishSLSuccessful and publishVSSuccessful:
        return True
    return False


if __name__ == "__main__":
    main()
"""
Nex step  is to test the oreder status function and continue with the pipeline
"""