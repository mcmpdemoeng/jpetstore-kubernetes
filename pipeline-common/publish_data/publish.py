from load_data.devops_builds.builds import post_build_data
from load_data.devops_tests.tests import post_tests_data
from load_data.devops_deployments.deployments import post_deployment_data
from load_data.devops_secure.secure import post_vulnerabilities_scans
from common_utils import args_utils, loggers

import os, sys

PARSER = args_utils.parse_arguments()
ARGS = PARSER.parse_args()
LOGGER = loggers.create_logger_module("devops-intelligence-publisher")

TENANT_URL = os.getenv("TENANT_URL", "")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

INFO_MESSAGE = "Publishing data to DevOps Intelligence {0}."


def main():
    # check_flags = sum([1 if val == True else 0 for _, val in vars(ARGS).items()])
    if ARGS.build:
        LOGGER.info(INFO_MESSAGE.format("Builds"))
        result, err = post_build_data(TENANT_URL, BEARER_TOKEN)
        if not result:
            LOGGER.error("Error = Data couldn't be published.")
            return
        LOGGER.info("The data was published successfully.")
    if ARGS.test:
        LOGGER.info(INFO_MESSAGE.format("Tests"))
        result, err = post_tests_data(TENANT_URL, BEARER_TOKEN)
        if not result:
            LOGGER.error("Error = Data couldn't be published.")
            return
        LOGGER.info("The data was published successfully.")
    if ARGS.deploy:
        LOGGER.info(INFO_MESSAGE.format("Deployment"))
        result, err = post_deployment_data(TENANT_URL, BEARER_TOKEN)
        if not result:
            LOGGER.error("Error = Data couldn't be published.")
            return
        LOGGER.info("The data was published successfully.")
    if ARGS.secure:
        LOGGER.info(INFO_MESSAGE.format("Secure"))
        result, err = post_vulnerabilities_scans(TENANT_URL, BEARER_TOKEN)
        if not result:
            LOGGER.error(f"Error = Data couldn't be published")
            return
        LOGGER.info("The data was published successfully.")
    # if check_flags > 1:
    #     LOGGER.error("The script needs just one flag at a time.")
    if len(sys.argv) < 2:
        PARSER.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
