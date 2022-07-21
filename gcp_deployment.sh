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
    docker run --rm --network=host -e SONAR_HOST_URL="${SONARQUBE_HOST}" -e SONAR_LOGIN="${SONARQUBE_TOKEN}" -v "$(pwd)":/usr/src  sonarsource/sonar-scanner-cli -Dsonar.projectKey=petstore_jenkins_shared
    docker scan --accept-license --version
    docker scan --accept-license --login --token $SNYK_SCAN_TOKEN
    docker scan --accept-license  "${JPETSTOREWEB}:latest"
    docker scan --accept-license  "${JPETSTOREDB}:latest"
}

test() {
    java --version
    apk update && apk add apache-ant
    cd jpetstore
    ls
    ant runtest
    cd ..
    cp -r ./jpetstore/build/reports/TEST-*.xml /workspace/
    cat /workspace/TEST-org.springframework.samples.jpetstore.domain.CartTest.xml
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
            echo "-b, --build               build application"
            echo "-s, --secure              secure application"
            echo "-t, --test                test application"
            echo "-d, --deploy              deploy application"
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
            echo "BUILD_DURATION_TIME=$((enddate - startdate)) s"
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
            echo "Secure application"
            # secure
            shift
            ;;
        -t|--test)
            echo "Test application in GCP"
            startdate=$(date +%s)
            (
                set -e
                test
            )
            enddate=$(date +%s)
            echo "TEST_DURATION_TIME=$((enddate - startdate)) s"
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
            shift
            ;;
        -pd|--push-devops)
            echo "Push data to DevOps Intelligence"
            shift
            ;;
        *)
            break
            ;;
    esac
done
shift "$(($OPTIND -1))"