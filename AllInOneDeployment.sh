#!/bin/bash
#sleep 120

echo "Updating order status..."

API_URL="${TENANT_URL/.multicloud-ibm.com/-api.multicloud-ibm.com}api/fulfillment/prov_posthook_response"
PAYLOAD='{"additionalMessage":"Provisioning Completed. Check build _BUILDconsole","comments":"Provisioned Completed.","orderNumber":"_ORD","serviceFulfillmentId":"_FUL","status":"ProvisionCompleted","version":""}'
PAYLOAD="${PAYLOAD/_ORD/"$ORDER_NUMBER"}"
PAYLOAD="${PAYLOAD/_FUL/"$FULFILLMENT_ID"}"
PAYLOAD="${PAYLOAD/_BUILD/"$BUILD_URL"}"


echo "$PAYLOAD" > payload.json
cat payload.json

API_USERNAME="username: ${USER_ID}"
API_KEY="apikey: ${USER_API_KEY}"

curl --request POST $API_URL \
-H "${API_USERNAME}" \
-H "${API_KEY}" \
-H "Content-Type: application/json" \
-d @payload.json

echo "\nSleeping 2 min..."

rm -f payload.json

sleep 120



echo "Cleaning up workspace...."

rm -rf jpetstore-kubernetes
rm -rf gh_2.5.2_linux_386
rm -f gh_2.5.2_linux_386.tar.gz

wget -q https://github.com/cli/cli/releases/download/v2.5.2/gh_2.5.2_linux_386.tar.gz

tar -xf gh_2.5.2_linux_386.tar.gz

echo ${GITHUB_ACCESS_TOKEN} > github_token

./gh_2.5.2_linux_386/bin/gh auth login -h GitHub.com --with-token < github_token

git clone "${GITHUB_REPO_URL}"

cd jpetstore-kubernetes
python3 -m pip install -r ./publish_data/requirements.txt 



#!/bin/sh


echo "Building application..."


build(){
  
  JPETSTOREWEB="${DOCKER_USERNAME}/jpetstoreweb:${BUILD_NUMBER}"
  JPETSTOREDB="${DOCKER_USERNAME}/jpetstoredb:${BUILD_NUMBER}"
  
  docker build -t $JPETSTOREWEB ./jpetstore
  docker build -t $JPETSTOREDB .
  docker logout
  docker login -u "${DOCKER_USERNAME}" -p "${DOCKER_PASSWORD}"
  docker push $JPETSTOREWEB
  docker push $JPETSTOREDB
  docker rmi $JPETSTOREWEB
  docker rmi $JPETSTOREDB
}


startdate=$(date +%s)
(
  set -e
  build
)
enddate=$(date +%s)

errorCode=$?

if [ $errorCode -ne 0 ]; then
	echo "Application build has failed"
    echo "failed" >> build_status
else
	echo "Application build has succeded"
	echo "success" >> build_status	
fi


echo "$((enddate - startdate))" >> build_duration_time



#!/bin/sh

export TENANT_SYSTEM_USER_NAME="${USER_ID}"
export TENANT_SYSTEM_USER_API_KEY="${USER_API_KEY}"

echo "Reading order details from marketplace..."

python3 marketplace_order_reader.py

export mysql_url=$(cat db_url | base64)
export mysql_user=$(cat db_user | base64)
export petstore_host=$(cat fqdn)
export mysql_password=$(cat db_password | base64)

echo "Testing application..."


test(){
  cd jpetstore
  ant runtest
  cd ..
}

startdate=$(date +%s)
(
	set -e
    test
)
enddate=$(date +%s)

errorCode=$?

if [ $errorCode -ne 0 ]; then
	echo "Application test has failed"
    echo "failed" >> test_status
else
	echo "Application test has succeded"
	echo "success" >> test_status	
fi



echo "$((enddate - startdate))" >> test_duration_time

deploy(){

  echo "Deploying application..."
  
  NAMESPACE="jppetstore"
  
  docker logout
  docker login -u "${DOCKER_USERNAME}" -p "${DOCKER_PASSWORD}"
  kubectl delete job jpetstoredb --ignore-not-found -n $NAMESPACE --kubeconfig tmp_kube_config
  helm package --destination $JENKINS_HOME/modernpets ./helm/modernpets
  helm upgrade --install --wait --set image.repository=${DOCKER_USERNAME} --set image.tag=$BUILD_NUMBER --set mysql.url=$mysql_url --set mysql.username=$mysql_user --set mysql.password=$mysql_password --set isDBAAS=True --set isLB=False --set httpHost=$petstore_host --namespace=$NAMESPACE --create-namespace $NAMESPACE $JENKINS_HOME/modernpets/modernpets-0.1.5.tgz --kubeconfig tmp_kube_config
  
  echo "\n\nYour application is available at http://jpetstore-web.${petstore_host}\n\n"
  
  app=$(kubectl get  ingress -n $NAMESPACE --kubeconfig tmp_kube_config | base64 | tr -d '\r')
  app_decoded=$(kubectl get  ingress -n $NAMESPACE --kubeconfig tmp_kube_config | tr -d '\r')
  echo app running at $app_decoded
  chmod +x result.sh
  ./result.sh ${app}

}


startdate=$(date +%s)
(
	set -e
    deploy
)
enddate=$(date +%s)


if [ $errorCode -ne 0 ]; then
	echo "Application deploy has failed"
    echo "failed" >> deploy_status
else
	echo "Application deploy has succeded"
	echo "success" >> deploy_status	
fi

echo "$((enddate - startdate))" >> deploy_duration_time




export TENANT_SYSTEM_USER_NAME="${USER_ID}"
export TENANT_SYSTEM_USER_API_KEY="${USER_API_KEY}"

export SERVICE_NAME="petstore_on_aks_jenkins"

export BUILD_DURATION_TIME=$(cat build_duration_time)
export BUILD_ENGINE="Jenkins"
export BUILD_STATUS=$(cat build_status)
export BUILD_HREF="${BUILD_URL}"

export BEARER_TOKEN="${TENANT_BEARER_TOKEN}"
export RUN_ID="${BUILD_TAG}"
export BRANCH="${GIT_BRANCH}"
export REPO="${GIT_URL}"
export COMMIT="${GIT_COMMIT}"

export TEST_STATUS=$(cat test_status)
export TEST_DURATION_TIME=$(cat test_duration_time)
export TEST_TYPE="unit"
export TEST_FILE_TYPE="xunit"
export TEST_ENGINE="XUNIT"
export TEST_ENVIRONMENT="Jenkins"
export TEST_RELEASE="${BUILD_TAG}"
export TEST_FILE="TEST-org.springframework.samples.jpetstore.domain.CartTest.xml"

export DEPLOYMENT_STATUS=$(cat deploy_status)
export DEPLOY_DURATION_TIME=$(cat deploy_duration_time)
export PROVIDER="Azure"

export petstore_host=$(cat fqdn)
export DEPLOYMENT_HOSTNAME="http://jpetstore-web.${petstore_host}"
export DEPLOYMENT_SERVICE_ID="petstore_on_aks_jenkins"
export DEPLOYMENT_HREF="http://jpetstore-web.${petstore_host}"

echo "Reading existing tokens..."

#cd .. # root

mkdir -p devops_tokens

cd devops_tokens

if [ -f "DEPLOY_TOKEN" ]; then
	echo "Deploy token found!"
    export DEPLOY_TOKEN=$(cat DEPLOY_TOKEN)
fi

if [ -f "BUILD_TOKEN" ]; then
	echo "Build token found!"
    export BUILD_TOKEN=$(cat BUILD_TOKEN)
fi

if [ -f "TEST_TOKEN" ]; then
	echo "Test token found!"
    export TEST_TOKEN=$(cat TEST_TOKEN)
fi

cd .. # root

#cd jpetstore-kubernetes

echo "Publishing data into the tenant...."

cp ./jpetstore/build/reports/TEST-*.xml ./publish_data

cd ./publish_data

python3 publish.py --deploy --build --test

echo "Storing devops tokens files..."

ls

# cd .. # publish_data

cd .. # root


if [ -f "./jpetstore-kubernetes/publish_data/DEPLOY_TOKEN" ]; then
	cp ./publish_data/DEPLOY_TOKEN ./devops_tokens
	echo "Deploy token saved!"
fi

if [ -f "./jpetstore-kubernetes/publish_data/BUILD_TOKEN" ]; then
	cp ./publish_data/BUILD_TOKEN ./devops_tokens
	echo "Build token saved!"
fi

if [ -f "./jpetstore-kubernetes/publish_data/TEST_TOKEN" ]; then
	cp ./publish_data/TEST_TOKEN ./devops_tokens
	echo "Test token saved!"
fi



ns=$(kubectl get ns --kubeconfig tmp_kube_config | grep monitoring | awk '{print $1}')

if [ -z "$ns" ] || [ "$ns" != "monitoring" ]; then
	kubectl create ns monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ./prometheus -n monitoring --kubeconfig tmp_kube_config
    sleep 1m
    kubectl apply -f ./alertmanager/AlertManagerConfigmap.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ./alertmanager/AlertTemplateConfigMap.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ./alertmanager/Deployment.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ./alertmanager/Service.yaml -n monitoring --kubeconfig tmp_kube_config
fi
