import requests
import logging
import time
from jsonpath_ng.ext import parse

from abc import abstractclassmethod, ABC

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("Default")

    
def web_request( url, requestMethod=requests.get, LOGGER=logging.getLogger(__name__), **kwargs ):
    """
        Use This function in the same way as requests library.
        Note: Send the request method as a function parameter as shown in the default 'requestMethod'

        returns: tuple( response, errorString )
    """
        
    try:
        response = requestMethod( url=url, **kwargs )
        response_is_sucessful = response.status_code >= 200 and response.status_code < 300
        if response_is_sucessful:
        
            return response,  ""
        LOGGER.warn(
            f"""Non 200 response from {url}
            args: {kwargs}                
            method:  {requestMethod.__name__}
            response: {response.text}
            response status code: {response.status_code}
            """
        )
    
        return response, f"status code: {response.status_code}"

    except requests.Timeout or requests.ConnectionError or requests.ConnectTimeout:
        LOGGER.error(
            f"""Fail to make request
                args: {kwargs}
                error: Fail to connect to {url}  
                """
        )
        
        return None,  f"Fail to connect to {url}"

    except Exception as error:
        ## TODO: add the line number and the filename to the error log
        LOGGER.error(
            f"""Fail to make request to {url} (No params included)
                args: {kwargs}
                error:  {error.args} 
                """
        )
        return None, f"Fail - {error} "



def try_web_request( url, requestMethod=requests.get, LOGGER=logging.getLogger(__name__), max_attempts=3, secondsToRetry=60, endProcessIfFail=False,  **kwargs ):
    for attempt in range(max_attempts):

        try:
            if attempt != 0: LOGGER.info(f"Retring, attempt: {attempt}")
            response, error = web_request( url=url, requestMethod=requestMethod, LOGGER=LOGGER, **kwargs )
            
            if response == None:
                continue

            remote_server_error =  response.status_code > 499 and response.status_code < 600
            if not remote_server_error:
                return response, error

            LOGGER.warning(f"Unable to get response from {url}")
            time.sleep(secondsToRetry)
            
        except BaseException as error:
            LOGGER.error(f"Fail on attempt {attempt}: {error.args}")
            return None, error

    error = f"Fail to get response from '{url}' after {max_attempts} attempts in {secondsToRetry * max_attempts } seconds" 
    LOGGER.warning( error )

    if endProcessIfFail:
        exit(1)
    return None, error

def sanitazeTenantUrl(tenantUrl:str, urlType:str ="url"):
    """
    tenantUrl: string
        Example: http://mcmp-learn.multicloud-ibm.com/

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


##TODO: this function is duplicated in this file, fix that
def get_value_from_dict( dictData, jsonpath_pattern ):

    if not dictData:
        return None

    expression = parse( jsonpath_pattern )
    matches = [ match.value for match in expression.find(dictData) ]
    if matches:
        return matches if len(matches) > 1 else matches[0]
    return None

def parse_value_from_dict( dictData, jsonpath_pattern ):

    if not dictData:
        return None

    expression = parse( jsonpath_pattern )
    matches = [ match.value for match in expression.find(dictData) ]
    if matches:
        return matches[0] 
    return None

class EMPService:

    def __init__():
        pass
    

    @staticmethod
    def get_order_details(tenantApi, userID, apikey, orderID, endProcessIfFail=False):
        url = f"{tenantApi}v5/api/orders/{orderID}/detail"
        headers = {
            "username" : userID,
            "apikey": apikey
        }

        response, _ = try_web_request(url=url, headers=headers)
        try:
            return response.json()
           
        
        except BaseException as error:
            print(f"Fail to get order details \nError: -> {error. __class__. __name__} : {error.args}")
            if endProcessIfFail:
                exit(1)


    @staticmethod
    def get_order_provider(tenantApi, userID, apikey, orderID,endProcessIfFail=False ):
        url = f"{tenantApi}/v5/api/orders/{orderID}/detail"
        headers = {
            "username" : userID,
            "apikey": apikey
        }
        LOGGER.info("Getting order provier")
        response, _ = try_web_request(url=url, headers=headers)
        try:
            jsonResponse = response.json()

            provider =  get_value_from_dict( jsonResponse, jsonpath_pattern="$.data.orderItems[0].providerCode" )
            LOGGER.info(f"Provier '{provider}' found ")
            return provider
    
        except BaseException as error:
            print(f"Fail to get provider from order details \nError:-> {error. __class__. __name__} : {error.args}")
            if endProcessIfFail:
                exit(1)

    @staticmethod
    def get_service_instance_details(tenantApi, userID, apikey, SID, endProcessIfFail=False, provider='azure' ):
        url = f"{tenantApi}v3/api/services/{provider}/{SID}"
        headers = {
            "username" : userID,
            "apikey": apikey
        }
        response, _  = try_web_request( url=url, headers=headers )
        try :
            return response.json()
        
        except BaseException as error:
            print(f"Fail to get service instance details \nError:-> {error. __class__. __name__} : {error.args}")
            if endProcessIfFail:
                exit(1)


    @staticmethod
    def get_service_outputs( tenantApiUrl, userID, apikey, serviceInventoryID, maxRetries=3, endProcessIfFail=False ):
        tenantApiUrl = sanitazeTenantUrl( tenantApiUrl, urlType="api" )
        ENDPOINT = f"{tenantApiUrl}icb/inventory/v1/api/services/azure/{serviceInventoryID}/outputparams"
        headers = {
            "username": userID,
            "apikey": apikey
        }
        response , _ = try_web_request( url=ENDPOINT, max_attempts=maxRetries, headers=headers, endProcessIfFail=endProcessIfFail )
        
        try:
            return response.json()
        
        except BaseException as error:
            print(f"Fail to get service instance details \nError:-> {error. __class__. __name__} : {error.args}")
            if endProcessIfFail:
                exit(1)
    

    @staticmethod
    def get_value_from_dict( dictData, jsonpath_pattern ):
        #TODO: fix this for the vsphere get os case it is returning two values
        if not dictData:
            return None

        expression = parse( jsonpath_pattern )
        matches = [ match.value for match in expression.find(dictData) ]
        if matches:
            return matches if len(matches) > 1 else matches[0]
        return None


    @staticmethod
    def update_post_provisioning_hook( tenantApiUrl, userID, apikey, orderID, fulfillmentID, status="Completed", endProcessIfFails=False ):

        tenantApiUrl = sanitazeTenantUrl( tenantApiUrl, urlType="api" )
        ENDPOINT = f"{tenantApiUrl}api/fulfillment/prov_posthook_response"

        payload = {
            "orderNumber": orderID,
            "serviceFulfillmentId": fulfillmentID,
            "status": status,
            "version": "3.0",
            "comments": "",
            "additionalMessage": "",
            "forceUpdate": True
        }
        headers = {
            'username': userID,
            'apikey': apikey,
            'Content-Type': 'application/json'
        }


        response, _ = try_web_request( requestMethod=requests.post, url=ENDPOINT, headers=headers, payload=payload)
        if response:
            LOGGER.info(f"Successfully updated order {orderID} in {tenantApiUrl}")
            return
        elif endProcessIfFails:
            exit(1) 


    @staticmethod
    def update_pre_provisioning_hook():
        pass


    @staticmethod
    def getPatternsDetails(tenantApiUrl, userID, apikey, endProcessIfFail=False, orderID=False ):
        """params:
                tenantApiUrl [string] -> tenant api url
                userID [string]       -> user id with the necesary EMP permissions to access orders
                apikey [string]       -> api key of user
        """
    
        tenantApiUrl =  sanitazeTenantUrl( tenantApiUrl, urlType="api" )
        ENDPOINT     =  f"{tenantApiUrl}icb/inventory/v5/patterns"

        headers = {
            "username": userID,
            "apikey": apikey
        }
        response, _ = try_web_request( requestMethod=requests.get, url=ENDPOINT, headers=headers, endProcessIfFail=endProcessIfFail )
        bad_request = response.status_code >= 400
        
        if endProcessIfFail and bad_request:
            exit(1)

        try:
            jsonData = response.json()
            if orderID:
                
                for patternOrder in jsonData.get( "result", [] ):
                    
                    if patternOrder.get("orderId", "") == orderID:
                        
                        return patternOrder

                return None
            
            return jsonData

        
        except BaseException as error:
            print(f"Fail to get patterns from {ENDPOINT} details \nError:-> {error. __class__. __name__} : {error.args}")
            if endProcessIfFail:
                exit(1)
    



def getResouceDetails(tenantApiUrl, userID, apikey, orderID, endProcessIfFail=False):
    """params:
            tenantApiUrl [string] -> tenant api url
            userID [string]       -> user id with the necesary EMP permissions to access orders
            apikey [string]       -> api key of user
            orderID [string]      -> To specify an order
    """
    tenantApiUrl =  sanitazeTenantUrl( tenantApiUrl, urlType="api" )
    ENDPOINT     =  f"{tenantApiUrl}api/"

    headers = {
        "username": userID,
        "apikey": apikey
    }

    orderDetails = EMPService.get_service_instance_details( tenantApi=tenantApiUrl, userID=userID, apikey=apikey, SID=orderID, endProcessIfFail=endProcessIfFail )

    return orderDetails
###########

class VirutalMachine( ABC ):
    
    @abstractclassmethod
    def __init__(self, tenantApi, userID, apikey, SID, orderID):
        ...

    @abstractclassmethod
    def get_os():
        ...
    
    @abstractclassmethod
    def get_linux_creds():
        ...

    @abstractclassmethod
    def get_windows_creds():
        ...

    @abstractclassmethod
    def get_creds():
        ...

###########


class AzureVirtualMachine( VirutalMachine, EMPService ):
    
    def __init__( self, tenantApi, userID, apikey, SID, orderID ):

        self.tenantApi = sanitazeTenantUrl(tenantApi, urlType="api")
        self.userID = userID
        self.apikey = apikey
        self.SID = SID
        self.orderID = orderID
        self.orderDetails = self.get_order_details( tenantApi=self.tenantApi, userID=self.userID, apikey=self.apikey, orderID=self.orderID,endProcessIfFail=True )
        self.serviceInstanceDetails = self.get_service_instance_details( self.tenantApi, self.userID, self.apikey, self.SID, endProcessIfFail=True )
        self.os = self.get_os()

    def get_os( self ):

        path = '$.resources[?( @.resourceType=~".*virtual_machine.*" )].templateOutputProperties[?( @.name=="Source Image Reference")].value[0].offer'
        os = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=path )
        
        return 'windows' if 'windows' in os.lower() else 'linux'

    
    def get_linux_creds( self ):
        
        ipAddressPath = '$.resources[?( @.resourceType=~".*virtual_machine.*" )].templateOutputProperties[?( @.name=="Public Ip Address")].value'
        ipAddress = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=ipAddressPath )

        adminUsernamePath = '$.resources[?( @.resourceType=~".*virtual_machine.*" )].templateOutputProperties[?( @.name=="Admin Username")].value'
        adminUsername = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=adminUsernamePath )

        self.outputsDetails = self.get_service_outputs( tenantApiUrl=self.tenantApi, userID=self.userID, apikey=self.apikey, serviceInventoryID=self.SID, maxRetries=4 )
        adminPasswordPath = '$.result.templateOutputParams[?( @.paramName=="admin_password" )].paramValue'
        adminPassword = self.get_value_from_dict( self.outputsDetails, jsonpath_pattern=adminPasswordPath )

        return ipAddress, adminUsername, adminPassword


    def get_windows_creds( self ):
        print("get_windows_creds needs to be implemented")
        pass


    def get_creds( self  ):

        if self.os.lower() == 'windows':
            return self.get_windows_creds()
        
        elif self.os.lower() == 'linux': 
            return self.get_linux_creds()
        
        else:
            raise Exception(f"Unknown os_type '{self.os}' \n Allowed types: ['linux' , 'windows']")




#TODO: implement this class as part of the VirutalMachine protocol
class VsphereVirtualMachine( VirutalMachine, EMPService ):
    def __init__(self, tenantApi, userID, apikey, SID, orderID ) -> None:

        self.tenantApi = sanitazeTenantUrl(tenantApi, urlType="api")
        self.userID = userID
        self.apikey = apikey
        self.SID = SID
        self.orderID = orderID
        self.orderDetails = self.get_order_details( tenantApi=self.tenantApi, userID=self.userID, apikey=self.apikey, orderID=self.orderID,endProcessIfFail=True )
        self.serviceInstanceDetails = self.get_service_instance_details( self.tenantApi, self.userID, self.apikey, self.SID, endProcessIfFail=True, provider='hashicorpvsphere1cMPg81Q' )
        self.os = self.get_os( )


    def get_os( self ):

        path = '$.resources[?( @.resourceType=~".*virtual_machine.*" )].templateOutputProperties[?( @.name=="Guest Id")].value'
        os = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=path )[0]

        return 'windows' if 'windows' in os.lower() else 'linux'

    def get_linux_creds( self ):
        """
            Return: (  IP_ADDRESS, USER_NAME, USER_PASSWORD )
        """
        
        #Default Ip Address path for service instance Details
        ipaddressPath = '$.resources[?( @.resourceType=~".*virtual_machine.*" )].templateOutputProperties[?( @.name=="Default Ip Address")].value'
        ip = get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=ipaddressPath )[1]

        outputDetails = self.get_service_outputs( tenantApiUrl=self.tenantApi, userID=self.userID, apikey=self.apikey, serviceInventoryID=self.SID, maxRetries=6 )
        #admin username
        adminUsernamePath = '$.result.templateOutputParams[?( @.paramName=="admin_username" )].paramValue'
        adminUsername = get_value_from_dict( outputDetails, jsonpath_pattern=adminUsernamePath )
        
        #admin password
        adminPasswordPath = '$.result.templateOutputParams[?( @.paramName=="admin_password" )].paramValue'
        adminPassword = get_value_from_dict( outputDetails, jsonpath_pattern=adminPasswordPath)
        
        return ip, adminUsername, adminPassword


    def get_windows_creds( self ):
        print("get windows creds  needs to be implemeted for Vsphere class")


    def get_creds( self ):
        if self.os.lower() == 'windows':
            return self.get_windows_creds()
        
        elif self.os.lower() == 'linux': 
            return self.get_linux_creds()
        
        else:
            raise Exception(f"Unknown os_type '{self.os}' \n Allowed types: ['linux' , 'windows']")


#TODO: implement this class as part of the VirutalMachine protocol
class VRAVirtualMachine(VirutalMachine, EMPService):
    def __init__(self, tenantApi, userID, apikey, SID, orderID ) -> None:
        self.tenantApi = sanitazeTenantUrl(tenantApi, urlType="api")
        self.userID = userID
        self.apikey = apikey
        self.SID = SID
        self.orderID = orderID
        self.orderDetails = self.get_order_details( tenantApi=self.tenantApi, userID=self.userID, apikey=self.apikey, orderID=self.orderID,endProcessIfFail=True )
        self.serviceInstanceDetails = self.get_service_instance_details( self.tenantApi, self.userID, self.apikey, self.SID, endProcessIfFail=True, provider='vra' )
        self.os = self.get_os()

    def get_os(self):
        #TODO: IF service instance details request fails we need to know how to handle it

        path = '$.resources[?( @.resourceType=~".*Cloud.vSphere.Machine.*" )].templateOutputProperties[?( @.name=="OsType")].value'
        os = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=path )

        return 'windows' if 'windows' in os.lower() else 'linux'


    def get_linux_creds( self ):
        
        #TODO: this needs to be tested
        IPpath = '$.resources[?( @.resourceType=~".*Cloud.vSphere.Machine.*" )].primaryInfo[?( @.name=="address")].value'
        ip = self.get_value_from_dict( self.serviceInstanceDetails, jsonpath_pattern=IPpath )

        usernamePath = 'data.orderItems[?(@.serviceOfferingName=~"*.CentO.*" )].configInfo[?( @.configGroup=="General" )].config[? ( @.configId=="vm_user" ) ].values[0].value'
        adminUsername = self.get_value_from_dict( self.orderDetails, jsonpath_pattern=usernamePath )
        
        # passwordPath = 'data.orderItems[?(@.serviceOfferingName=~"*.CentO.*" )].configInfo[?( @.configGroup=="General" )].config[? ( @.configId=="vm_user" ) ].values[0].value'
        adminPassword = "Usesshkeyforthisservice"
        
        return ip, adminUsername, adminPassword


    def get_windows_creds( self ):
        print("windows vra case need to be implemented")


    def get_creds( self ):
        if self.os.lower() == 'windows':
            return self.get_windows_creds()
        
        elif self.os.lower() == 'linux': 
            return self.get_linux_creds()
        
        else:
            raise Exception(f"Unknown os_type '{self.os}' \n Allowed types: ['linux' , 'windows']")




