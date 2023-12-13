#!/bin/bash
#sleep 120

#### 1 - 2
echo "Updating order status..."
if [[ -f ORDER_NUMBER.txt ]] && [[ $ORDER_NUMBER == "" ]]
then
    export ORDER_NUMBER=$(cat ORDER_NUMBER.txt)
    export FULFILLMENT_ID=$(cat FULFILLMENT_ID.txt)
fi
API_URL="${TENANT_URL/.multicloud-ibm.com/-api.multicloud-ibm.com}api/fulfillment/prov_posthook_response"
PAYLOAD='{"additionalMessage":"Provisioning Completed. Check build _BUILDconsole","comments":"Provisioned Completed.","orderNumber":"_ORD","serviceFulfillmentId":"_FUL","status":"ProvisionCompleted","version":""}'
PAYLOAD="${PAYLOAD/_ORD/"$ORDER_NUMBER"}"
PAYLOAD="${PAYLOAD/_FUL/"$FULFILLMENT_ID"}"
PAYLOAD="${PAYLOAD/_BUILD/"$BUILD_URL"}"

echo $ORDER_NUMBER > ORDER_NUMBER.txt
echo $FULFILLMENT_ID > FULFILLMENT_ID.txt

echo "$PAYLOAD" > payload.json
cat payload.json

API_USERNAME="username: ${USER_ID}"
API_KEY="apikey: ${USER_API_KEY}"

curl --request POST $API_URL \
-H "${API_USERNAME}" \
-H "${API_KEY}" \
-H "Content-Type: application/json" \
-d @payload.json
### 1 - 2

rm -f payload.json

pip3 install --upgrade pip
python3 -m pip install -r ../pipeline-common/publish_data/requirements.txt 
### 3
echo "Building application..."

export JPETSTOREWEB="${DOCKER_USERNAME}/jpetstoreweb:${BUILD_NUMBER}"
export JPETSTOREDB="${DOCKER_USERNAME}/jpetstoredb:${BUILD_NUMBER}"

build(){
  docker build -t $JPETSTOREWEB ../jpetstore
  docker build -t $JPETSTOREDB ../
  docker logout
  docker login -u "${DOCKER_USERNAME}" -p "${DOCKER_PASSWORD}"
  docker push $JPETSTOREWEB
  docker push $JPETSTOREDB
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
### 4
export TENANT_SYSTEM_USER_NAME="${USER_ID}"
export TENANT_SYSTEM_USER_API_KEY="${USER_API_KEY}"

echo "Reading order details from marketplace..."

python3 ../pipeline-common/marketplace_order_reader.py

export mysql_url=$(cat db_url | base64 -w0)
export mysql_user=$(cat db_user | base64 -w0)
export petstore_host=$(cat fqdn)
export mysql_password=$(cat db_password | base64 -w0)

echo "Testing application..."

test(){
  cd ../jpetstore
  ant runtest
  cd ../pipeline-jenkins
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

secure(){
    echo "Secure application tests..."
    cd ../jpetstore
    docker run --rm --network=host -e SONAR_HOST_URL="${SONARQUBE_HOST}" -e SONAR_LOGIN="${SONARQUBE_TOKEN}" -v "$(pwd)":/usr/src  sonarsource/sonar-scanner-cli -Dsonar.projectKey=petstore_jenkins_shared
    cd ../pipeline-jenkins
    docker scan --accept-license --version
    docker scan --accept-license --login --token $SNYK_SCAN_TOKEN
    docker scan --accept-license --json $JPETSTOREDB >> db.json
    docker scan --accept-license --json $JPETSTOREWEB >> web_app.json
    export DB_JSON_REPORT_PATH="db.json"
    export WEB_JSON_REPORT_PATH="web_app.json"
    python3 ../pipeline-common/publish_data/publish.py --secure
    return 0
}

#(
    # set -ex
    # secure
#)

docker rmi $JPETSTOREWEB
docker rmi $JPETSTOREDB

echo "Deploying application..."

deploy(){

  echo "Deploying application..."
  ls
  
  NAMESPACE="jppetstore"  

  docker logout
  docker login -u "${DOCKER_USERNAME}" -p "${DOCKER_PASSWORD}"
  kubectl delete job jpetstoredb --ignore-not-found -n $NAMESPACE --kubeconfig tmp_kube_config
  helm package --destination $JENKINS_HOME/modernpets ../helm/modernpets
  
  helm upgrade --install --wait --set image.repository=$DOCKER_USERNAME --set image.tag=$BUILD_NUMBER --set mysql.url=$mysql_url --set mysql.username=$mysql_user --set mysql.password=$mysql_password --set isDBAAS=True --set isLB=False --set httpHost=$petstore_host --namespace=$NAMESPACE --create-namespace $NAMESPACE --kubeconfig tmp_kube_config $JENKINS_HOME/modernpets/modernpets-0.1.5.tgz
  
  echo "Your application is available at http://jpetstore-web.${petstore_host}"
  
  app=$(kubectl get  ingress -n $NAMESPACE --kubeconfig tmp_kube_config | base64 | tr -d '\r')
  app_decoded=$(kubectl get  ingress -n $NAMESPACE --kubeconfig tmp_kube_config | tr -d '\r')
  echo app running at $app_decoded
  chmod +x ../result.sh
  ../result.sh ${app}
}


startdate=$(date +%s)
(
    set -ex
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
### 4

export TENANT_SYSTEM_USER_NAME="${USER_ID}"
export TENANT_SYSTEM_USER_API_KEY="${USER_API_KEY}"

export SERVICE_NAME="RT_petstore_on_aks_jenkins"

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


echo "Publishing data into the tenant...."

pwd

cp ../jpetstore/build/reports/TEST-*.xml ../pipeline-common/publish_data

cd ../pipeline-common/publish_data

python3 publish.py --deploy --build --test

cd ../../pipeline-jenkins

echo "Deploy monitoring..."

ns=$(kubectl get ns --kubeconfig tmp_kube_config | grep monitoring | awk '{print $1}')

if [ -z "$ns" ] || [ "$ns" != "monitoring" ]; then
    kubectl create ns monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ../prometheus -n monitoring --kubeconfig tmp_kube_config
    sleep 1m
    kubectl apply -f ../alertmanager/AlertManagerConfigmap.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ../alertmanager/AlertTemplateConfigMap.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ../alertmanager/Deployment.yaml -n monitoring --kubeconfig tmp_kube_config
    kubectl apply -f ../alertmanager/Service.yaml -n monitoring --kubeconfig tmp_kube_config
fi
