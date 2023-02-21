import os

def deploy_petstore_monitoring( kubeconfigPath="tmp_kube_config" ) -> bool:
    print("Deploy monioring...")
    commandsList = [
       f"kubectl create ns monitoring --kubeconfig {kubeconfigPath}",
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
        