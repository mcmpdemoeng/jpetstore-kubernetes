## REQUIRE 
## ENV: mysql_url(host)  mysql_user  mysql_password  base64_kubeconfig  fqdn  namespace, cluster_name, cluster_resource_group
kubeconfigFile="tmp_kube_config"
imageTag="latest"
base64_mysql_url=$( echo ${mysql_url} | base64 -w 0)
base64_mysql_user=$( echo ${mysql_user} | base64 -w 0)
base64_mysql_password=$( echo ${mysql_password} | base64 -w 0 )

set -e

az login --identity
az aks get-credentials --resource-group ${cluster_resource_group} --name  ${cluster_name}

echo Credentials configured!!!



kubectl delete job jpetstoredb --ignore-not-found -n ${namespace} 

helm package --destination modernpets helm/modernpets

set -e
helm upgrade --install --wait --set image.repository=mcmpdemo --set image.tag=${imageTag} --set mysql.url=${base64_mysql_url} --set mysql.username="${base64_mysql_user}" --set mysql.password="${base64_mysql_password}" --set isDBAAS=True --set isLB=False --set httpHost="${fqdn}" --namespace ${namespace} --create-namespace ${namespace}   modernpets/modernpets-0.1.5.tgz --debug

echo Your application will be available on http://jpetstore-web.${fqdn}