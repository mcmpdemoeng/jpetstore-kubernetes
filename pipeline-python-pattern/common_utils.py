import logging as LOGGER
import requests
import subprocess
import os
import json
import logging

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
        print(f"Error: Kube config ('tmp_kube_config') not found in local path")
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


def get_logger():
    return logging

LICENSES = [{
			"License Name": "New BSD",
			"Package Name": "github.com/fsnotify/fsnotify",
			"Package Version": "v1.5.1",
			"Status": "Allowed"
		},
		{
			"License Name": "Apache 2.0",
			"Package Name": "github.com/Luzifer/go-openssl/v3",
			"Package Version": "v3.1.0",
			"Status": "Allowed"
		},
		{
			"License Name": "JWT",
			"Package Name": "github.com/golang-jwt/jwt/v4",
			"Package Version": "v4.4.0",
			"Status": "Allowed"
		},
		{
			"License Name": "Perks",
			"Package Name": "github.com/beorn7/perks",
			"Package Version": "v1.0.1",
			"Status": "Allowed"
		},
		{
			"License Name": "Lestrrat-go",
			"Package Name": "github.com/lestrrat-go/backoff/v2",
			"Package Version": "v2.0.8",
			"Status": "Allowed"
		},
		{
			"License Name": "Cenkalti",
			"Package Name": "github.com/cenkalti/backoff/v4",
			"Package Version": "v4.1.2",
			"Status": "Allowed"
		},
		{
			"License Name": "Felixge",
			"Package Name": "github.com/felixge/httpsnoop",
			"Package Version": "v1.0.2",
			"Status": "Allowed"
		},
		{
			"License Name": "Xxhash",
			"Package Name": "github.com/cespare/xxhash/v2",
			"Package Version": "v2.1.2",
			"Status": "Allowed"
		},
		{
			"License Name": "Semver",
			"Package Name": "github.com/blang/semver",
			"Package Version": "v3.5.1",
			"Status": "Allowed"
		},
		{
			"License Name": "Tollbooth",
			"Package Name": "github.com/didip/tollbooth",
			"Package Version": "v4.0.2",
			"Status": "Allowed"
		},
		{
			"License Name": "Go-stack",
			"Package Name": "github.com/go-stack/stack",
			"Package Version": "v1.8.1",
			"Status": "Allowed"
		},
		{
			"License Name": "Mozilla Public License 2.0",
			"Package Name": "github.com/hashicorp/errwrap",
			"Package Version": "v1.0.0",
			"Status": "Allowed"
		},
		{
			"License Name": "Simplified BSD",
			"Package Name": "github.com/magiconair/properties",
			"Package Version": "v1.8.6",
			"Status": "Allowed"
		},
		{
			"License Name": "GNU Lesser General Public License (LGPL) v2",
			"Package Name": "github.com/mitchellh/mapstructure",
			"Package Version": "v1.4.3",
			"Status": "Allowed"
		},
		{
			"License Name": "GTPL (Globus Toolkit)",
			"Package Name": "github.com/subosito/gotenv",
			"Package Version": "v1.2.0",
			"Status": "Allowed"
		},
		{
			"License Name": "IPL",
			"Package Name": "github.com/stretchr/testify",
			"Package Version": "v1.7.0",
			"Status": "Allowed"
		},
		{
			"License Name": "MIT",
			"Package Name": "github.com/stretchr/testify/assert",
			"Package Version": "v1.7.0",
			"Status": "Allowed"
		},
		{
			"License Name": "Apache 2.0",
			"Package Name": "github.com/dgrijalva/jwt-go",
			"Package Version": "v4.0.0",
			"Status": "Allowed"
		},
		{
			"License Name": "GNU Lesser General Public License (LGPL) v3",
			"Package Name": "github.com/go-ldap/ldap/v3",
			"Package Version": "v3.3.0",
			"Status": "Allowed"
		},
		{
			"License Name": "SQLX",
			"Package Name": "github.com/jmoiron/sqlx",
			"Package Version": "v1.3.0",
			"Status": "Allowed"
		}
	]