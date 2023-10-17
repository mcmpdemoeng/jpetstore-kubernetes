import os
import logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Monitoring")

def deploy_petstore_monitoring( kubeconfigPath="tmp_kube_config" ) -> bool:
    #TODO: Create monitoring ns if doesnt exist
    LOGGER.info("Deploy monioring...")
    error = create_kubernetes_namespace(kubeconfigPath="tmp_kube_config", namespace="monitoring")
    if error:
        
        return False

    commandsList = [
       f"kubectl apply -f ../prometheus -n monitoring --kubeconfig {kubeconfigPath}",
       f"sleep 1m",
       f"kubectl apply -f ../alertmanager/AlertManagerConfigmap.yaml -n monitoring --kubeconfig {kubeconfigPath}",
       f"kubectl apply -f ../alertmanager/AlertTemplateConfigMap.yaml -n monitoring --kubeconfig {kubeconfigPath}",
       f"kubectl apply -f ../alertmanager/Deployment.yaml -n monitoring --kubeconfig {kubeconfigPath}",
       f"kubectl apply -f ../alertmanager/Service.yaml -n monitoring --kubeconfig {kubeconfigPath}"
    ]
    successfulOperation = executeCommandsList(commandsList)
    if successfulOperation:
        print("Monitoring successfully installled")
        return True
    return False



def executeCommandsList( commandsList ):
    for command in commandsList:
        returncode = os.system(command)
        if returncode != 0:
            print(
                f"""
                Waring: Could not execute {command}
                returncode: {returncode}
                """
            )
            return False
        
    return True

def create_kubernetes_namespace(kubeconfigPath="tmp_kube_config", namespace="monitoring"):
    """
    Creates the kubernentes namespace only if doesn't exists.\n
    Returns an error string if fails
    """
    try:
        ##TODO: we need to halde the case the kubecofig is not correct and causes the error
        returncode = os.system(f"kubectl get ns {namespace} --kubeconfig {kubeconfigPath} ")
        
        namespaceAlreadyExists = returncode == 0
        if namespaceAlreadyExists:
            return

        returncode = os.system(f"kubectl create ns {namespace} --kubeconfig {kubeconfigPath}")
        if returncode != 0:
            raise Exception(f"Error: Fail to create namespace {namespace}")
    except BaseException as error:
        return str(error)
