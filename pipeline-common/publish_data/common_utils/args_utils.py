import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process command line arguments")
    parser.add_argument(
        "-t", "--test", action="store_true", help="This argument enables the test service of DevOps Intelligence."
    )
    parser.add_argument(
        "-s", "--secure", action="store_true", help="This argument enables the secure service of DevOps Intelligence."
    )
    parser.add_argument(
        "-b", "--build", action="store_true", help="This argument enables the test service of DevOps Intelligence.."
    )
    parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help="This argument enables the deployment service of DevOps Intelligence..",
    )
    return parser
