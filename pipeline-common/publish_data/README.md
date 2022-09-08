# Explore DevOps Intelligence Scripts

These scripts are used to push data into DevOps Intelligence for Build, Test, and Deploy. These scripts are intended to be used in a pipeline workflow of CI/CD.

# Prerequisites

You will need the following in your worker to use these scripts:

- [Python 3.10](https://www.python.org/)
- Install Python `requirements.txt`

# Usage

In order to use the application you just need to set up all the environment variables used in the application for each stage. Then, you can run this command depending on your needs:

```bash
python ./publish_data/publish.py --test
```

Flags that can be used:
- `--build`
- `--test`
- `--deploy`
- `--secure`
  Please consider:

  Instead of displaying the docker scans results on the logs, you will need to output the scans as a json file as follows:
  docker scan $IMAGE_NAME --json >> sample_output.json
  export the following env vars:

  SECURE_TOKEN: secure token generated from DI
  DB_JSON_REPORT_PATH: path to the json file that resulted from the docker scan of the db image
  WEB_JSON_REPORT_PATH: path to the json file that resulted from the docker scan of the web app image
