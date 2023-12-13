import argparse
import os
from jsonpath_ng.ext import parse
import logging

from common_utils import make_web_request, sanitazeTenantUrl

logging.basicConfig(level=os.getenv('LOGGIN_LEVEL_NUMBER', 20 ))
LOGGER = logging.getLogger("petstore-catalog-deploy")


parser = argparse.ArgumentParser()

parser.add_argument("-t", "--tenant", dest = "tenantApiUrl", default = "https://mcmp-learn-api.multilcoud-ibm.com", help="Tenant API base url\nEx: https://mcmp-learn-api.multilcoud-ibm.com", required=True)
parser.add_argument("-k", "--apikey", dest = "apikey", default = "", help="Apikey of the defined user" )
parser.add_argument("-u", "--userid", dest = "userid", default = "", help="User id of the tenant" )
parser.add_argument("-o", "--orderid", dest="orderID", default="", help="Order Id"  )
args = parser.parse_args()


def get_service_invetory_id(tenantUrl: str, userid: str, apikey:str, orderNumber:str ) -> dict:
    """Gets serviceInventoryID"""
    
    tenantApiUrl = sanitazeTenantUrl( tenantUrl=tenantUrl, urlType='api')
    ENDPOINT = f"{tenantApiUrl}v5/api/orders/{orderNumber}/detail"

    headers = {
        "username": userid, 
        "apikey": apikey
    }
    
    response, _, _= make_web_request( url=ENDPOINT, headers=headers )
    if not response or response.status_code != 200:
        raise Exception("Fail to read order deatails and get serviceInventoryId")
    
    jsonData = response.json()

    return  [ match.value for match in parse("$.data.orderItems[0].services[0].serviceInventoryId").find(jsonData)][0]


def read_infrastructure_details(tenantUrl: str, userid: str, apikey:str,  serviceInventoryId:str ) -> dict:
    """Gets AKS cluster kubeconfig and routing zone url"""
    
    tenantApiUrl = sanitazeTenantUrl( tenantUrl=tenantUrl, urlType='api' )
    ENDPOINT = f"{tenantApiUrl}v3/api/services/azure/{serviceInventoryId}"

    headers = {
        "username": userid, 
        "apikey": apikey
    }
    

    response, _, _= make_web_request( url=ENDPOINT, headers=headers )
    
    if not response or response.status_code !=200:
        raise Exception("fail to get infrastructure details")
    jsonData = response.json()

    kubeconfig =  [ match.value for match in parse("$.resources[?(@.resourceType == 'azurerm_kubernetes_cluster')].templateOutputProperties[?(@.name == 'Kube Config Raw')].value").find(jsonData)][0]
    routingZone = [ match.value for match in parse("$.resources[?(@.resourceType == 'azurerm_kubernetes_cluster')].templateOutputProperties[?(@.name == 'Http Application Routing Zone Name')].value").find(jsonData)][0]
    return kubeconfig, routingZone



def create_file_with_content(file_path, content):
    # Get the directory path from the file path
    directory_path = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Create and write the content to the file
    with open(file_path, 'w') as file:
        file.write(content)




def main():
    LOGGER.info("Getting service inventory id")
    serviceInventoryId = get_service_invetory_id(tenantUrl=args.tenantApiUrl, userid=args.userid, apikey=args.apikey, orderNumber=args.orderID)
    LOGGER.info(f"Done - {serviceInventoryId}")
    
    LOGGER.info("Getting infrastructure details ")
    kubeconfig, httpRoutingZone = read_infrastructure_details( tenantUrl=args.tenantApiUrl, userid=args.userid, apikey=args.apikey, serviceInventoryId=serviceInventoryId )
    LOGGER.info("Done")

    LOGGER.info(f"Creating ./kubeconfig file")
    create_file_with_content( "./kubeconfig", kubeconfig )
    LOGGER.info("Done")

    LOGGER.info(f"Creating ./httpRoutingZone file")
    create_file_with_content( "./httpRoutingZone",  httpRoutingZone )
    LOGGER.info("Done")


if __name__ == "__main__":
    main()