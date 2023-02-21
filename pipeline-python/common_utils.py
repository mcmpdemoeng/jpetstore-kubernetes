import logging as LOGGER
import requests
import subprocess
import os
import json
def sanitazeTenantUrl(tenantUrl:str, urlType:str ="url"):
    """
    tenantUrl: string
        Example: http://mcmp-learn.multicloud-ibm.com

    urlType: string -> 'url' (web tenant url) | 'api' (api endpoint)
    """
    splitUrlList = tenantUrl.split(".")
    if urlType  ==  "url":
        #TODO: we are validating  2 time if ends with -api
        if "-api" in splitUrlList[0]:
            splitUrlList[0] = splitUrlList[0].replace("-api", "")
            tenantUrl = ".".join(splitUrlList)

        if tenantUrl.endswith("/"):
            return tenantUrl

        else:
            return f"{tenantUrl}/"


    elif urlType  ==  "api":
        
        if not "-api" in splitUrlList[0]:
            splitUrlList[0] = f"{splitUrlList[0]}-api"
        
        apiUrl = ".".join(splitUrlList)

        if apiUrl.endswith("/"):
            return f"{apiUrl}"
        else:
            return f"{apiUrl}/"


def file_exists(path:str)-> bool:
    fileExists = os.path.exists("tmp_kube_config")
    if not fileExists:
        print(f"Error: Kube config ('tmp_kube_config') not found in local paht")
        localFiles = subprocess.getoutput("ls")
        print(f"ls output:\n{localFiles}")
    return fileExists


def make_web_request(url="", payload={}, headers={}, requestMethod=requests.get, logToIBM=False, params={} ):

    try:
        # TODO - Chage the static arguments for dynamic ones
        # TODO - in case of a gateway time out error 504 (statuscode) retry
        response = requestMethod(url=url, json=payload, headers=headers, params=params)
        if response.status_code >= 200 and response.status_code < 300:
            return response, True, ""

        LOGGER.warn(
            f"""Non 200 response from {url}
            headers: {headers}
            payload: {payload}
            method:  {requestMethod.__name__}
            response:{response.text}
            response status code: {response.status_code}
            """
        )

        return response, False, f"status code: {response.status_code}"

    except requests.Timeout or requests.ConnectionError or requests.ConnectTimeout:
        LOGGER.error(
            f"""Fail to make request
                headers: {headers}
                payload: {payload}
                error: Fail to connect to {url}  
                """
        )

        return None, False, f"Fail to connect to {url}"

    except Exception as error:
        LOGGER.error(
            f"""Fail to make request to {url}
                headers: {headers}
                payload: {payload}
                error:  {error}  """
        )

        return None, False, f"Fail - {error} "

def makeWebRequest(requestMethod=requests.get, logToIBM=False,  **kwargs ):
    
    try:
        # TODO - Chage the static arguments for dynamic ones
        response = requestMethod(**kwargs)
        if response.status_code <= 200 and response.status_code < 300:
            return response, True, ""

        LOGGER.warn(
            f"""Non 200 response from {kwargs.get('url')}\n
            request arguments: {kwargs.items()}
            method:  {requestMethod.__name__}
            response:{response.text}
            response status code: {response.status_code}"""
        )

        return response, False, f"status code: {response.status_code}"

    except requests.Timeout or requests.ConnectionError or requests.ConnectTimeout:
        LOGGER.error(
            f"""Fail to make request\n
                request arguments: {kwargs.items()}  """
        )

        return None, False, f"Fail to connect to {kwargs.get('url')}"

    except Exception as error:
        LOGGER.error(
            f"""Fail to make request to {kwargs.get('url')} \n
                request arguments: {kwargs.items()}
                error:  {error}  """
        )

        return None, False, f"Fail - {error} "


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True