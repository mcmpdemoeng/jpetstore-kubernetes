import os, requests, base64


def get_order_number_details(tenant_system_user_name, tenant_system_user_api_key, order_number, tenant_api_url):
    data = {}

    ENDPOINT = "{0}v5/api/orders/{1}/detail".format(tenant_api_url, order_number)
    headers = {"username": tenant_system_user_name, "apikey": tenant_system_user_api_key}
    response = requests.get(url=ENDPOINT, headers=headers)
    if response.status_code != 200 and response.status_code != 201:
        return False, str(response.text)

    response = response.json()

    # service instance id
    data["service_instance_id"] = response["data"]["orderItems"][0]["services"][0]["serviceInventoryId"]

    # database password
    configs = response["data"]["orderItems"][0]["configInfo"]
    inputs = None

    infrastructure_name = response["data"]["orderItems"][0]["serviceOfferingName"]

    for c in configs:
        if "parameters" in str(c["configGroup"]):
            inputs = c["config"]

    for param in inputs:
        if param["configId"] == "administratorPassword":
            data["db_password"] = param["values"][0]["value"]

    return True, data


def get_service_details(tenant_system_user_name, tenant_system_user_api_key, service_instance_id, tenant_api_url):
    ENDPOINT = "{0}v3/api/services/azure/{1}".format(tenant_api_url, service_instance_id)
    headers = {"username": tenant_system_user_name, "apikey": tenant_system_user_api_key}
    response = requests.get(url=ENDPOINT, headers=headers)

    if response.status_code != 200 and response.status_code != 201:
        return False, str(response.text)

    return True, response.json()


if __name__ == "__main__":
    try:
        print("Generating keys...")
        tenant_system_user_name = os.getenv("TENANT_SYSTEM_USER_NAME")
        tenant_system_user_api_key = os.getenv("TENANT_SYSTEM_USER_API_KEY")
        order_number = os.getenv("ORDER_NUMBER")
        tenant_api_url = os.getenv("TENANT_URL")

        tenant_api_url = tenant_api_url.replace(".multicloud-ibm.com", "-api.multicloud-ibm.com")

        error, order_details = get_order_number_details(
            tenant_system_user_name, tenant_system_user_api_key, order_number, tenant_api_url
        )
        if not error:
            print("Error [Order] = " + order_details)
            exit()

        service_instance_id = order_details["service_instance_id"]

        error, service_details = get_service_details(
            tenant_system_user_name, tenant_system_user_api_key, service_instance_id, tenant_api_url
        )

        if not error:
            print("Error [Service] = " + service_details)
            exit()

        fqdn = None
        kubeconfig = None
        db_url = None
        db_user = None
        db_server_name = None
        db_password = order_details["db_password"]

        for r in service_details["resources"]:

            # Get kubeconfig infor and FQDN
            if r["resourceType"] == "azurerm_kubernetes_cluster":
                for output in r["templateOutputProperties"]:

                    if output["name"] == "Http Application Routing Zone Name":
                        fqdn = output["value"]

                    if output["name"] == "Kube Config Raw":
                        kubeconfig = output["value"]
                        

            # Get database user, password and url
            if r["resourceType"] == "azurerm_mysql_server":

                db_server_name = r["name"]

                for output in r["templateOutputProperties"]:

                    if output["name"] == "Fqdn":
                        db_url = output["value"]
                    if output["name"] == "Administrator Login":
                        db_user = output["value"]

        # Save files
        db_user = db_user + "@" + db_url
        file_names = ["tmp_kube_config", "fqdn", "db_url", "db_user", "db_password"]
        file_contents = [kubeconfig, fqdn, db_url, db_user, db_password]

        for i in range(len(file_names)):
            tmp_file = open(file_names[i], "w")
            tmp_file.write(file_contents[i])
            tmp_file.close()
        print("All keys were generated.")

    except Exception as err:
        print("Error = " + str(err))
