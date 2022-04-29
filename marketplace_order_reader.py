import requests
import base64
import os

def get_order_number_details(tenant_system_user_name,tenant_system_user_api_key,order_number,tenant_api_url):
    
    data = {}

    ENDPOINT = "{0}v5/api/orders/{1}/detail".format(tenant_api_url, order_number)
    headers = { 'username': tenant_system_user_name, 'apikey': tenant_system_user_api_key}
    response = requests.get(url=ENDPOINT, headers=headers)
    response = response.json()

    # service instance id
    data["service_instance_id"] = response["data"]["orderItems"][0]["services"][0]["serviceInventoryId"]

    # database password
    configs = response["data"]["orderItems"][0]["configInfo"]
    inputs = None

    for c in configs:
        if c["configGroup"] == "Petstore Infrastructure on Azure AKS Parameters":
            inputs = c["config"]

    for param in inputs:
        if param["configId"] == "administratorLoginPassword":
            data["db_password"] = param["values"][0]["value"]

    return data

def get_service_details(tenant_system_user_name,tenant_system_user_api_key,service_instance_id,tenant_api_url):
    ENDPOINT = "{0}v3/api/services/azure/{1}".format(tenant_api_url, service_instance_id)
    headers = { 'username': tenant_system_user_name, 'apikey': tenant_system_user_api_key}   
    response = requests.get(url=ENDPOINT, headers=headers)
    return response.json()

if __name__ == "__main__":

    tenant_system_user_name = os.getenv("tenant_system_user_name")
    tenant_system_user_api_key = os.getenv("tenant_system_user_api_key")
    order_number = os.getenv("order_number")
    tenant_api_url = os.getenv("tenant_api_url")

    order_details = get_order_number_details(tenant_system_user_name,tenant_system_user_api_key,order_number,tenant_api_url)
    
    service_instance_id = order_details["service_instance_id"]
    
    service_details = get_service_details(tenant_system_user_name,tenant_system_user_api_key,service_instance_id,tenant_api_url)

    fqdn = None
    kubeconfig = None
    db_url = None
    db_user = None
    db_server_name = None
    db_password = order_details["db_password"]

    for r in service_details["resources"]:

        # Get kubeconfig infor and FQDN
        if r["resourceType"] == "Microsoft.ContainerService/ManagedClusters":
            for output in r["templateOutputProperties"]:
                
                if output["type"] == "properties":
                    fqdn = output["value"]["Addon Profiles"]["Http Application Routing"]["Config"]["HTTP Application Routing Zone Name"]

                if output["type"] == "kubeconfig" and output["value"]["kubeconfigs"][0]["name"] == "clusterAdmin":
                    kubeconfig = output["value"]["kubeconfigs"][0]["value"]
                    kubeconfig = str(base64.b64decode(kubeconfig), "utf-8")

        # Get database user, password and url 
        if r["resourceType"] == "Microsoft.DBforMySQL/servers":

            db_server_name = r["name"]
            
            for output in r["templateOutputProperties"]:

                if output["type"] == "properties":

                    db_url = output["value"]["Fully Qualified Domain Name"]
                    db_user = output["value"]["Administrator Login"] + "@" + db_server_name
                    
    # Save files
    file_names =    [ "tmp_kube_config.txt", "fqdn", "db_url", "db_user", "db_password" ]
    file_contents = [ kubeconfig, fqdn, db_url, db_user, db_password ]
        
    for i in range(len(file_names)):
        tmp_file = open(file_names[i], "w")
        tmp_file.write(file_contents[i])
        tmp_file.close()
