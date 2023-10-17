import os, requests
import common_utils
import logging
import MondernopsServices

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("OrderReader")


##TODO: We can wrap all this into a orderReader class

def get_order_details(tenant_user_id, tenant_system_user_api_key, order_number, tenant_api_url, maxRetries=4, currentReties=0):
    """
    Returns a dictionary with 'db_password', 'service_instance_id' keys.
    Ends the process if an error occurs
    """
    LOGGER.info("Reading order Details")
    ENDPOINT = f"{tenant_api_url}v5/api/orders/{order_number}/detail"
    headers = {
        "username": tenant_user_id, 
        "apikey": tenant_system_user_api_key
    }
    response, isSuccessfulResponse, _  = common_utils.make_web_request( requestMethod=requests.get, headers=headers, url=ENDPOINT )
    
    serverTimeout = response.status_code == 504

    if serverTimeout:
        LOGGER.warning("Warning: Time out getting petstore service instance id")
        currentReties += 1
        if currentReties <= maxRetries:
            get_order_details( tenant_user_id, tenant_system_user_api_key, order_number, tenant_api_url, maxRetries, currentReties )
    
        else:
            LOGGER.error(f"Fail to get service instance id, max retries reached '{maxRetries}'")
            exit(1)
    
    if not isSuccessfulResponse:
        LOGGER.error("Error: Fail to get service instance id")
        exit(1)
    
    isValidJson = common_utils.validateJSON( response.text )
    if not isValidJson:
        LOGGER.error(f"Error: Expecting a json response from {ENDPOINT} and got:\n{response.text}")
        exit(1)
    data = response.json()
    details = parse_petstore_order_details( data )
    LOGGER.info("Done reading order Details")
    return details


def parse_petstore_order_details(jsonData):
    """
    params:
        jsonData(dict): json response body of '{tenant_api_url}v5/api/orders/{order_number}/detail' 

    returns: 
        Dictionary with 'db_password', 'service_instance_id' keys.
        **In case of failure it exits the process**
    """
    try:
        data = {}
        data["service_instance_id"] = jsonData["data"]["orderItems"][0]["services"][0]["serviceInventoryId"]
        
        #Get the database password
        configs = jsonData["data"]["orderItems"][0]["configInfo"]
        for c in configs:
            if "parameters" in str(c["configGroup"]):
                inputs = c["config"]

        for param in inputs:
            if param["configId"] == "administratorPassword":
                data["db_password"] = param["values"][0]["value"]

        return data

    except:
        LOGGER.error("Error: Fail to parse petstore order details (parse_petstore_order_details)")
        LOGGER.error(f"Data to parse: \n{jsonData}")
        exit(1)


def get_petstore_service_instance_details( tenant_system_user_id, tenant_system_user_api_key, service_instance_id, tenant_api_url, maxRetries=4, currentReties=0 ):
    
    LOGGER.info("Reading service instace details")
    ENDPOINT = f"{tenant_api_url}v3/api/services/azure/{service_instance_id}"
    headers = {
        "username": tenant_system_user_id, 
        "apikey": tenant_system_user_api_key
    }
    response, isSuccessfulResponse, _  = common_utils.make_web_request( requestMethod=requests.get, url=ENDPOINT, headers=headers )
    timeOutError = response.status_code == 504
    if timeOutError:
        LOGGER.warning("Warning: Time out getting petstore service instance details")
        if currentReties >= maxRetries:
            LOGGER.error(f"Error: time out error, tried {currentReties} times")
            exit(1)
        currentReties += 1
        LOGGER.info("Retrying to get petstore service instance details")
        get_petstore_service_instance_details( tenant_system_user_id, tenant_system_user_api_key, service_instance_id, tenant_api_url, currentReties=currentReties)
    
    if not isSuccessfulResponse:
        LOGGER.error("Error:  'get_petstore_service_instance_details' func was unable to get a successful response")
        exit(1)
    
    isValidJson = common_utils.validateJSON( response.text )
    if not isValidJson:
        LOGGER.error(f"Error: Expecting a json response from {ENDPOINT} and got:\n{response.text}")
        exit(1)

    data = response.json()
    
    details = parse_service_instance_details(data)
    LOGGER.info("Done reading service instance details")

    return details


def parse_service_instance_details( jsonData ):
    fqdn = ""
    kubeconfig = ""
    db_url = ""
    db_user = ""
    LOGGER.info(f"Number of resources in order: {len(jsonData['resources'])}" )

    for resouce in jsonData["resources"]:
        # Get kubeconfig infor and FQDN
        if resouce["resourceType"] == "azurerm_kubernetes_cluster":
            for output in resouce["templateOutputProperties"]:

                if output["name"] == "Http Application Routing Zone Name":
                    fqdn = output["value"]

                if output["name"] == "Kube Config Raw":
                    kubeconfig = output["value"]
                    

        # Get database user, password and url
        if resouce["resourceType"] == "azurerm_mysql_server":

            for output in resouce["templateOutputProperties"]:

                if output["name"] == "Fqdn":
                    db_url = output["value"]
                if output["name"] == "Administrator Login":
                    db_user = output["value"]

    db_user = db_user + "@" + db_url

    return {
        "tmp_kube_config": kubeconfig,
        "fqdn": fqdn,
        "db_url": db_url,
        "db_user": db_user,
    }

def read_petstore_order( tenantApiUrl, tenantUserId, tenantUserApikey, orderNumber, createKubeconfigFile=True, kubeconfigFileName="tmp_kube_config" ):
    tenantApiUrl = common_utils.sanitazeTenantUrl(tenantApiUrl, urlType="api")


    # Read pattern details
    patternDetails = MondernopsServices.EMPService.getPatternsDetails( tenantApiUrl=tenantApiUrl, userID=tenantUserId, apikey=tenantUserApikey, orderID=orderNumber, endProcessIfFail=True )
    
    # Identify order id and SOI for AKS and mysql
    AKSClusterSID = patternDetails.get('chainedSOIs', {})[0].get('SID', '')
    MYSQLSID = patternDetails.get('chainedSOIs', {})[1].get('SID', '')
    MYSQLOrderID = patternDetails.get('chainedSOIs', {})[1].get('orderItemNumber', '')

    # make the 3 calls to get the data form soi and order details 
    AKSClusterSIDInfo = MondernopsServices.EMPService.get_service_instance_details( tenantApi=tenantApiUrl, userID=tenantUserId, apikey=tenantUserApikey, SID=AKSClusterSID, endProcessIfFail=True )
    
    kubeconfig = MondernopsServices.parse_value_from_dict(
        dictData=AKSClusterSIDInfo,
        jsonpath_pattern='resources[?( @.resourceType=="azurerm_kubernetes_cluster" )].templateOutputProperties[?( @.name=="Kube Config Raw" )].value'
    )

    fqdn = MondernopsServices.parse_value_from_dict(
        dictData=ord,
        jsonpath_pattern='resources[?( @.resourceType=="azurerm_kubernetes_cluster" )].templateOutputProperties[?( @.name=="Fqdn" )].value'
    )

    MYSQLSIDInfo = MondernopsServices.EMPService.get_service_instance_details( tenantApi=tenantApiUrl, userID=tenantUserId, apikey=tenantUserApikey, SID=MYSQLSID, endProcessIfFail=True )
    
    mysqlURL = MondernopsServices.get_value_from_dict(
        dictData=MYSQLOrderInfo,
        jsonpath_pattern='resources[?( @.resourceType=="azurerm_mysql_server" )].templateOutputProperties[?( @.name=="Fqdn" )].value'
    )
    mysqlUser =  MondernopsServices.get_value_from_dict(
        dictData=MYSQLSIDInfo,
        jsonpath_pattern='resources[?( @.resourceType=="azurerm_mysql_server" )].templateOutputProperties[?( @.name=="Administrator Login" )].value'
    )
    
    MYSQLOrderInfo = MondernopsServices.EMPService.get_order_details( tenantApi=tenantApiUrl, userID=tenantUserId, apikey=tenantUserApikey, orderID=MYSQLOrderID, endProcessIfFail=True )
    
    mysqlPassword = MondernopsServices.parse_value_from_dict(
        dictData=MYSQLOrderInfo,
        jsonpath_pattern='data.orderItems[?( @.serviceOfferingName=~".*mysql.*" )].configInfo[?( @.configGroup=~".*mysql.*parameters.*" )].config[?( @.configId=="serverPassword" )].values[0].value'
    )
    
    if createKubeconfigFile:
        tmp_file = open(kubeconfigFileName, "w")
        tmp_file.write(kubeconfig)
        tmp_file.close()

    return {
            "tmp_kube_config": kubeconfig,
            "fqdn": fqdn,
            "db_url": mysqlURL,
            "db_user": mysqlUser,
            "db_password": mysqlPassword
        }


if __name__ == "__main__":
    LOGGER.info(
        read_petstore_order(
            tenantApiUrl="https://learnmodernops-api.bridge.kyndryl.com",
            tenantUserId="625090e80f8c6927409061d4",
            tenantUserApikey="5fb95995-a348-508a-a409-46b29e2429d2",
            orderNumber="KJCMMHBFDS"
        )
    )