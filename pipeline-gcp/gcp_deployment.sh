#!/bin/bash

export JPETSTOREWEB="${DOCKER_USERNAME}/jpetstoreweb"
export JPETSTOREDB="${DOCKER_USERNAME}/jpetstoredb"

build() {
    export TIMESTAMP=`date -u +%Y%m%d%H%M%S`
    export BUILD_TAG="${BUILD_ID}-${BRANCH_NAME}-${SHORT_SHA}-${TIMESTAMP}"
    
    echo "BUILD_TAG=${BUILD_TAG}"
    echo "JPETSTOREWEB_TAG=${JPETSTOREWEB}:${BUILD_TAG}"
    echo "JPETSTOREDB_TAG=${JPETSTOREDB}:${BUILD_TAG}"
    docker build -t "${JPETSTOREWEB}:${BUILD_TAG}" -t "${JPETSTOREWEB}:latest" ./jpetstore
    docker build -t "${JPETSTOREDB}:${BUILD_TAG}" -t "${JPETSTOREDB}:latest" .
    docker login -u "${DOCKER_USERNAME}" -p "${DOCKER_PASSWORD}"
    docker push "${JPETSTOREWEB}:${BUILD_TAG}"
    docker push "${JPETSTOREWEB}:latest"
    docker push "${JPETSTOREDB}:${BUILD_TAG}"
    docker push "${JPETSTOREDB}:latest"
    docker logout
}

secure() {
    echo "JPETSTOREWEB_TAG=${JPETSTOREWEB}:latest"
    echo "JPETSTOREDB_TAG=${JPETSTOREDB}:latest"

    cd jpetstore
    docker run --rm --network=host -e SONAR_HOST_URL="${SONARQUBE_HOST}" -e SONAR_LOGIN="${SONARQUBE_TOKEN}" -v "$(pwd)":/usr/src  sonarsource/sonar-scanner-cli -Dsonar.projectKey=$SYSTEM_DEFINITIONNAME
    cd ..
    
    docker scan --accept-license --version
    docker scan --accept-license --login --token $SNYK_SCAN_TOKEN
    docker scan --accept-license --json "${JPETSTOREWEB}:latest" >> /workspace/web_app.json || echo 0
    docker scan --accept-license --json "${JPETSTOREDB}:latest" >> /workspace/db.json || echo 0
}

testing() {
    cd jpetstore
    ls
    ant runtest
    cd ..
    cp -r ./jpetstore/build/reports/TEST-*.xml /workspace/
    cat /workspace/TEST-org.springframework.samples.jpetstore.domain.CartTest.xml
}

deploy() {
    MYSQL_USERNAME=$(echo $MYSQL_USERNAME | base64)
    MYSQL_PASSWORD=$(echo $MYSQL_PASSWORD | base64)
    MYSQL_URL=$(echo $MYSQL_URL | base64)
    NAMESPACE="jpetstore"
    kubectl delete job jpetstoredb --ignore-not-found -n $NAMESPACE --kubeconfig /workspace/.kube/config
    helm package --destination ./modernpets ./helm/modernpets
    helm upgrade --install --wait --set image.repository=${DOCKER_USERNAME} --set image.tag=latest --set mysql.url=${MYSQL_URL} --set mysql.username=${MYSQL_USERNAME} --set mysql.password=${MYSQL_PASSWORD} --set isDBAAS=True --set isLB=True --set httpHost=${PETSTORE_HOST} --namespace=${NAMESPACE} --create-namespace ${NAMESPACE} --kubeconfig /workspace/.kube/config ./modernpets/modernpets-0.1.5.tgz
    PETSTORE_HOST=$(kubectl get services/jpetstore-nodeport -o jsonpath='{.status.loadBalancer.ingress[0].ip}' -n $NAMESPACE)
    echo "http://${PETSTORE_HOST}" >> /workspace/fqdn
    echo "\n\nYour application is available at http://${PETSTORE_HOST}\n\n"
}

devops_intelligence() {
    export TENANT_URL="${TENANT_URL}"
    export TENANT_SYSTEM_USER_NAME="${USER_ID}"
    export TENANT_SYSTEM_USER_API_KEY="${USER_API_KEY}"

    export SERVICE_NAME="petstore_on_gcp"

    export BUILD_DURATION_TIME=$(cat /workspace/build_duration_time)
    export BUILD_ENGINE="Cloud Build GCP"
    export BUILD_STATUS=$(cat /workspace/build_status)
    export BUILD_HREF="https://console.cloud.google.com/cloud-build/builds;region=${LOCATION}/${BUILD_ID}?authuser=3&project=${PROJECT_ID}"

    export BEARER_TOKEN="${TENANT_BEARER_TOKEN}"
    export RUN_ID="$(echo $BUILD_ID | cut -c 1-8)"
    export BRANCH="${BRANCH_NAME}"
    export REPO="${REPO_NAME}"
    export COMMIT="${SHORT_SHA}"

    export TEST_STATUS=$(cat /workspace/test_status)
    export TEST_DURATION_TIME=$(cat /workspace/test_duration_time)
    export TEST_TYPE="unit"
    export TEST_FILE_TYPE="xunit"
    export TEST_ENGINE="XUNIT"
    export TEST_ENVIRONMENT="Cloud Build GCP"
    export TEST_RELEASE="$(echo $BUILD_ID | cut -c 1-8)"
    export TEST_FILE="TEST-org.springframework.samples.jpetstore.domain.CartTest.xml"

    export DB_JSON_REPORT_PATH="/workspace/db.json"
    export WEB_JSON_REPORT_PATH="/workspace/web_app.json"


    export DEPLOYMENT_STATUS=$(cat /workspace/deploy_status)
    export DEPLOY_DURATION_TIME=$(cat /workspace/deploy_duration_time)
    export PROVIDER="Google"

    export petstore_host=$(cat /workspace/fqdn)
    export DEPLOYMENT_HOSTNAME=$(cat /workspace/fqdn)
    export DEPLOYMENT_SERVICE_ID="petstore_on_gcp"
    export DEPLOYMENT_HREF=$(cat /workspace/fqdn)

    echo "Publishing data into the tenant...."

    pwd

    cp /workspace/TEST-*.xml ./pipeline-common/publish_data

    cd ./pipeline-common/publish_data

    python publish.py --test --build --secure --deploy

    cd ..
}

deploy_monitoring() {
    ns=$(kubectl get ns --kubeconfig /workspace/.kube/config | grep monitoring | awk '{print $1}')

    if [ -z "$ns" ] || [ "$ns" != "monitoring" ]; then
        kubectl create ns monitoring --kubeconfig /workspace/.kube/config
        kubectl apply -f ./prometheus -n monitoring --kubeconfig /workspace/.kube/config
        sleep 1m
        kubectl apply -f ./alertmanager/AlertManagerConfigmap.yaml -n monitoring --kubeconfig /workspace/.kube/config
        kubectl apply -f ./alertmanager/AlertTemplateConfigMap.yaml -n monitoring --kubeconfig /workspace/.kube/config
        kubectl apply -f ./alertmanager/Deployment.yaml -n monitoring --kubeconfig /workspace/.kube/config
        kubectl apply -f ./alertmanager/Service.yaml -n monitoring --kubeconfig /workspace/.kube/config
    fi
}

while test $# -gt 0; do
    case "$1" in
        -h|--help)
            echo "$package - attempt to capture frames"
            echo " "
            echo "$package [options] application [arguments]"
            echo " "
            echo "options:"
            echo "-h, --help                show brief help"
            echo "-b, --build               build application with docker"
            echo "-s, --secure              secure application with docker scan and sonarqube"
            echo "-t, --test                test application in a java environment"
            echo "-d, --deploy              deploy application into GKE Cluster"
            echo "--push-devops             push all info to DevOps Intelligence if all the variables are defined"
            echo "--deploy-monitoring       deploy prometheus monitoring on cluster selected"
            exit 0
            ;;
        -b|--build)
            echo "Build application in GCP"
            startdate=$(date +%s)
            (
            set -e
            build
            )
            enddate=$(date +%s)
            echo "BUILD_DURATION_TIME= $((enddate - startdate)) s"
            echo "$((enddate - startdate))" >> /workspace/build_duration_time
            errorCode=$?

            if [ $errorCode -ne 0 ]; then
                echo "Application build has failed"
                echo "failed" >> /workspace/build_status
            else
                echo "Application build has succeded"
                echo "success" >> /workspace/build_status
            fi
            shift
            ;;
        -s|--secure)
            echo "Secure application in GCP"
            startdate=$(date +%s)
            (
            set -e
            secure
            )
            enddate=$(date +%s)
            echo "SECURE_DURATION_TIME= $((enddate - startdate)) s"
            echo "$((enddate - startdate))" >> /workspace/secure_duration_time
            errorCode=$?

            if [ $errorCode -ne 0 ]; then
                echo "Application secure has failed"
                echo "failed" >> /workspace/build_status
            else
                echo "Application secure has succeded"
                echo "success" >> /workspace/build_status
            fi
            shift
            ;;
        -t|--test)
            echo "Test application in GCP"
            startdate=$(date +%s)
            (
                set -e
                testing
            )
            enddate=$(date +%s)
            echo "TEST_DURATION_TIME= $((enddate - startdate)) s"
            echo "$((enddate - startdate))" >> /workspace/test_duration_time
            errorCode=$?

            if [ $errorCode -ne 0 ]; then
                echo "Application test has failed"
                echo "failed" >> /workspace/test_status
            else
                echo "Application test has succeded"
                echo "success" >> /workspace/test_status	
            fi
            shift
            ;;
        -d|--deploy)
            echo "Deploy application in GCP"
            startdate=$(date +%s)
            (
                set -ex
                deploy
            )
            enddate=$(date +%s)
            echo "DEPLOY_DURATION_TIME= $((enddate - startdate)) s"
            echo "$((enddate - startdate))" >> /workspace/deploy_duration_time
            errorCode=$?

            if [ $errorCode -ne 0 ]; then
                echo "Application deploy has failed"
                echo "failed" >> /workspace/deploy_status
            else
                echo "Application deploy has succeded"
                echo "success" >> /workspace/deploy_status	
            fi
            shift
            ;;
        --push-devops)
            echo "Push data to DevOps Intelligence"
            devops_intelligence
            shift
            ;;
        --deploy-monitoring)
            echo "Deploy monitoring on cluster"
            deploy_monitoring
            shift
            ;;
        *)
            break
            ;;
    esac
done
shift "$(($OPTIND -1))"