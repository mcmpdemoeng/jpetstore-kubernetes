import requests
import json
import os

def get_order_number_details(tenant_system_user_name,tenant_system_user_api_key,petstore_order_number,tenant_api_url):
    ENDPOINT = "{0}v3/api/services/azure/{1}".format(tenant_api_url, petstore_order_number)
    headers = { 'username': tenant_system_user_name, 'apikey': tenant_system_user_api_key}   
    response = requests.get(url=ENDPOINT, headers=headers)
    return response.json()

if __name__ == "__main__":
    print("Script is working...")

    tenant_system_user_name = os.getenv("tenant_system_user_name")
    tenant_system_user_api_key = os.getenv("tenant_system_user_api_key")
    petstore_order_number = os.getenv("petstore_order_number")
    tenant_api_url = os.getenv("tenant_api_url")

    order_details = get_order_number_details(tenant_system_user_name,tenant_system_user_api_key,petstore_order_number,tenant_api_url)

    fqdn = None

    for r in order_details["resources"]:

        # Get kubeconfig infor and FQDN
        if r["resourceType"] == "Microsoft.ContainerService/ManagedClusters":
            for output in r["templateOutputProperties"]:
                if output["type"] == "properties":
                    fqdn = output["Addon Profiles"]["Http Application Routing"]["Config"]["HTTP Application Routing Zone Name"]

    print("\n%s\n"%(fqdn))
