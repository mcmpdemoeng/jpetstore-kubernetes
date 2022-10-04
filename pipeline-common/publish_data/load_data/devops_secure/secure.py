from datetime import datetime, timedelta
import json
import requests
import os
import traceback

from common_utils.constants import SECURE_TOKEN, loggers, SERVICE_NAME, VULNERABILITIES_URL_TEMPLATE, ImageScanTemplate, VulnerabilityTemplate
from load_data.tokens import tokens

LOGGER = loggers.create_logger_module("devops-intelligence-publisher")

TOKEN_API = "dash/api/dev_secops/v3/config/tokens"
SCANNED_BY = "snyk"
LIMIT_PER_REQUEST = 50

def __chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def __publish_image_scans(service_name,raw_json,tenant_url,secure_token):
    try:

        scan = ImageScanTemplate()
        scan.technical_service_name = service_name
        scan.technicalserviceoverride = True
        scan.provider_href = "https://snyk.io/"

        if not isinstance(raw_json, list):
            raw_json = [raw_json]

        vulnerabilities = []
        used = {}

        for report in raw_json:
            
            if "vulnerabilities" not in report: raise Exception(f"Missing attribute vulnerabilities from raw data. Service {service_name}")

            for vul_data in report["vulnerabilities"]:

                if vul_data["id"] not in used:

                    used[vul_data["id"]] = vul_data["id"]

                    vulnerabilities.append( VulnerabilityTemplate(
                        cvss=vul_data["cvssScore"],
                        description=vul_data["description"],
                        image_digest=vul_data["from"][0] if len(vul_data["from"]) > 0 else "",
                        pack_name=vul_data["packageName"],
                        pack_version=vul_data["version"],
                        pack_path=vul_data["name"],
                        severity=vul_data["severity"],
                        url=vul_data["references"][0]["url"] if len(vul_data["references"]) > 0 else "",
                        id=vul_data["id"]
                    ).__dict__)

        chunk_counter = 1

        for chunck in __chunks(vulnerabilities,LIMIT_PER_REQUEST):

            scan.technical_service_name = f"{scan.technical_service_name}-{chunk_counter}"

            chunk_counter +=1

            scan.vulnerable_image_scan = chunck

            date = (datetime.utcnow() - timedelta(days=0)).isoformat("T")+"Z"
            
            ENDPOINT = VULNERABILITIES_URL_TEMPLATE.format( tenant_url, SCANNED_BY, date )
            
            payload = scan.__dict__

            headers = { 'Authorization': 'TOKEN ' + secure_token, 'Content-Type': 'application/json', 'accept': 'application/json' }

            response = requests.post( data=json.dumps(payload), url= ENDPOINT, headers=headers )
            
            LOGGER.info( "Code = " + str(response.status_code))

            if response.status_code != 200 and response.status_code != 201:
                LOGGER.error( "Error = " +  str(response.text))
                return False, str(response.text)

        return True, ""
    except Exception as e:
        return False, str(e)
    

def post_vulnerabilities_scans( tenant_url, bearer_token ):
    try:

        DEVOPS_SECURE_TOKEN = (
            SECURE_TOKEN if SECURE_TOKEN != "" else tokens.get_token("SECURE", tenant_url, bearer_token, TOKEN_API).token
        )

        DB_JSON_REPORT_PATH = os.getenv("DB_JSON_REPORT_PATH",False)
        WEB_JSON_REPORT_PATH = os.getenv("WEB_JSON_REPORT_PATH",False)

        if not DB_JSON_REPORT_PATH: raise Exception("DB_JSON_REPORT_PATH value is missing")
        if not WEB_JSON_REPORT_PATH: raise Exception("WEB_JSON_REPORT_PATH value is missing")

        db_json_file = open(DB_JSON_REPORT_PATH,"r")
        web_json_file = open(WEB_JSON_REPORT_PATH,"r")

        db_report = json.load(db_json_file)
        web_report = json.load(web_json_file)

        db_result, db_err = __publish_image_scans(f"petstore_db_service",db_report,tenant_url,DEVOPS_SECURE_TOKEN)
        web_result, web_err = __publish_image_scans(f"petstore_web_service",web_report,tenant_url,DEVOPS_SECURE_TOKEN)

        return db_result and web_result, f"{db_err}{web_err}"

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(str(e))
        return False, str(e)
