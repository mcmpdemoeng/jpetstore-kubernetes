import os, requests
import common_utils
import logging

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

def read_petstore_order( tenantApiUrl, tenantUserId, tenantUserApikey, orderNumber, createKubeconfigFile=False, kubeconfigFileName="tmp_kube_config" ):
    tenantApiUrl = common_utils.sanitazeTenantUrl(tenantApiUrl, urlType="api")
    orderDetails = get_order_details(
        tenant_api_url=tenantApiUrl,
        tenant_system_user_api_key=tenantUserApikey,
        tenant_user_id=tenantUserId,
        order_number=orderNumber
    )

    serviceDetails = get_petstore_service_instance_details(
        tenant_api_url=tenantApiUrl,
        tenant_system_user_id=tenantUserId,
        tenant_system_user_api_key=tenantUserApikey,
        service_instance_id=orderDetails['service_instance_id']
    )

    if createKubeconfigFile:
        tmp_file = open(kubeconfigFileName, "w")
        tmp_file.write(serviceDetails['tmp_kube_config'])
        tmp_file.close()

    return {
            "tmp_kube_config": serviceDetails['tmp_kube_config'],
            "fqdn": serviceDetails['fqdn'],
            "db_url": serviceDetails['db_url'],
            "db_user": serviceDetails['db_user'],
            "db_password": orderDetails['db_password']
        }

if __name__ == "__main__":
    LOGGER.info(
        read_petstore_order(
            tenantApiUrl="https://mcmp-redthread-test1aws-uiauto.multicloud-ibm.com/",
            tenantUserId="",
            tenantUserApikey="",
            orderNumber=""
        )
    )