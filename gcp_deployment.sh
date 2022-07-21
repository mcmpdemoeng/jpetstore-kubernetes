#!/bin/bash

export JPETSTOREWEB="${DOCKER_USERNAME}/jpetstoreweb"
export JPETSTOREDB="${DOCKER_USERNAME}/jpetstoredb"
export TIMESTAMP=`date -u +%Y%m%d%H%M%S`
export BUILD_TAG="${BUILD_ID}-${BRANCH_NAME}-${SHORT_SHA}-${TIMESTAMP}"

build() {
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
            echo "BUILD_DURATION_TIME=$((enddate - startdate))"
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

            shift
            ;;
        -t|--test)
            echo "Test application in GCP"
            shift
            ;;
        -d|--deploy)
            echo "Deploy application in GCP"
            shift
            ;;
        *)
            break
            ;;
    esac
done
shift "$(($OPTIND -1))"