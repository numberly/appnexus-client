# -*- coding:utf-8-*-

import time

import requests

from appnexus import representations
from appnexus.cursor import Cursor
from appnexus.exceptions import (AppNexusException, RateExceeded, NoAuth,
                                 BadCredentials)
from appnexus.utils import normalize_service_name


class AppNexusClient(object):
    """Represents an active connection to the AppNexus API"""
    url = "http://api.appnexus.com/"
    test_url = "http://api-test.appnexus.com/"
    error_codes = {"RATE_EXCEEDED": RateExceeded}
    error_ids = {"NOAUTH": NoAuth}

    def __init__(self, username=None, password=None, debug=False, test=False,
                 representation=representations.raw):
        self.credentials = {"username": username, "password": password}
        self.token = None
        self.debug = debug
        self.representation = representation
        self.test = test

        self._generate_services()

    def _prepare_uri(self, service, **parameters):
        """Prepare the URI for a request

        :param service: The target service
        :type service: str
        :param kwargs: query parameters
        :return: The uri of the request
        """
        if self.test:
            base_url = self.test_url
        else:
            base_url = self.url
        for key, value in parameters.items():
            if isinstance(value, (list, tuple)):
                parameters[key] = ",".join([str(member) for member in value])

        list_formated_parameters = ["{}={}".format(key, value)
                                    for key, value in parameters.items()]
        query_parameters = "&".join(list_formated_parameters)
        if query_parameters:
            uri = "{}{}?{}".format(base_url, service, query_parameters)
        else:
            uri = "{}{}".format(base_url, service)
        return uri

    # shiro: Coverage is disabled for this function because it's mocked and it
    # doesn't need testing (for the moment) since it's a simple instruction
    def _handle_rate_exceeded(self):  # pragma: no cover
        """Handles rate exceeded errors"""
        time.sleep(10)

    def _send(self, send_method, service, data=None, **kwargs):
        """Send a request to the AppNexus API (used for internal routing)

        :param send_method: The method sending the request (usualy requests.*)
        :type send_method: function
        :param service: The target service
        :param data: The payload of the request (optionnal)
        :type data: anything JSON-serializable
        """
        valid_response = False
        raw = kwargs.pop("raw", False)

        while not valid_response:
            headers = dict(Authorization=self.token)
            uri = self._prepare_uri(service, **kwargs)
            if self.debug:  # pragma: no cover
                print('\n'.join(map(str, (headers, uri, data))))

            response = send_method(uri, headers=headers, json=data)
            response_data = response.json()
            try:
                self.check_errors(response, response_data["response"])
            except RateExceeded:
                self._handle_rate_exceeded()
            except NoAuth:
                self.update_token()
            else:
                valid_response = True
        if raw:
            return response_data
        return response_data["response"]

    def update_token(self):
        """Request a new token and store it for future use"""
        if self.debug:  # pragma: no cover
            print('updating token')
        if None in self.credentials.values():
            raise RuntimeError("Invalid Credentials")
        credentials = dict(auth=self.credentials)
        url = self.test_url if self.test else self.url
        response = requests.post(url + "auth",
                                 json=credentials)
        data = response.json()["response"]
        if "error_id" in data:
            if data["error_id"] == "NOAUTH":
                raise BadCredentials()
        if "error_code" in data:
            if data["error_code"] == "RATE_EXCEEDED":
                time.sleep(150)
                return
        if "error_code" in data or "error_id" in data:
            raise AppNexusException(response)
        self.token = data["token"]
        return self.token

    def check_errors(self, response, data):
        """check for errors and raise an appropriate error if needed"""
        if "error_id" in data:
            error_id = data["error_id"]
            if error_id in self.error_ids:
                raise self.error_ids[error_id](response)
        if "error_code" in data:
            error_code = data["error_code"]
            if error_code in self.error_codes:
                raise self.error_codes[error_code](response)
        if "error_code" in data or "error_id" in data:
            raise AppNexusException(response)

    def get(self, service, **kwargs):
        """retrieve data from AppNexus API"""
        return self._send(requests.get, service, **kwargs)

    def modify(self, service, json, **kwargs):
        """modify an AppNexus object"""
        return self._send(requests.put, service, json, **kwargs)

    def create(self, service, json, **kwargs):
        """create a new AppNexus object"""
        return self._send(requests.post, service, json, **kwargs)

    def append(self, service, json, **kwargs):
        kwargs.update({"append": True})
        return self.modify(service, json, **kwargs)

    def meta(self, service):
        """Retrieve meta-informations about a service"""
        return self.get(service + "/meta")

    def find(self, service, arguments=None, representation=None, **kwargs):
        representation = representation or self.representation
        args = arguments.copy() if arguments else dict()
        args.update(kwargs)
        return Cursor(self, service, representation, **args)

    def connect(self, username, password, debug=None, test=None,
                representation=None):
        self.credentials = {"username": username, "password": password}
        if test is not None:
            self.test = test
        if debug is not None:
            self.debug = debug
        if representation is not None:
            self.representation = representation

    def _generate_services(self):
        for service in services_list:
            normalized_name = normalize_service_name(service)
            snake_name = normalized_name.replace('-', '_')
            generated_service = Service(self, normalized_name)
            setattr(self, snake_name, generated_service)


services_list = ["AccountRecovery", "AdProfile", "Advertiser",
                 "AdQualityRule", "AdServer", "Brand", "Broker", "Browser",
                 "Campaign", "Carrier", "Category", "City", "ContentCategory",
                 "Country", "Creative", "CreativeFormat", "Currency",
                 "CustomModel", "CustomModelParser", "Deal", "DealBuyerAccess", 
                 "DealFromPackage", "DemographicArea", "DeviceMake",
                 "DeviceModel", "DomainAuditStatus", "DomainList",
                 "ExternalInvCode", "InsertionOrder", "InventoryAttribute",
                 "InventoryResold", "IpRangeService", "Label", "Language",
                 "LineItem", "Lookup", "NativeCustomKey", "ManualOfferRanking",
                 "MediaSubtype", "MediaType", "Member", "MobileApp",
                 "MobileAppInstance", "MobileAppInstanceList",
                 "MobileAppStore", "MemberProfile", "ObjectLimit",
                 "OperatingSystem", "OperatingSystemExtended",
                 "OperatingSystemFamily", "OptimizationZone", "Package",
                 "PackageBuyerAccess", "PaymentRule", "Pixel", "Placement",
                 "PlateformMember", "Profile", "ProfileSummary", "Publisher",
                 "Region", "ReportStatus", "Search", "Segment", "Site",
                 "TechnicalAttribute", "Template", "ThirdpartyPixel", "User",
                 "UsergroupPattern", "VisibilityProfile"]


class Service(object):

    def __init__(self, client, service):
        self.client = client
        self.service = service

    def find(self, arguments=None, **kwargs):
        return self.client.find(self.service, arguments, **kwargs)

    def find_one(self, arguments=None, **kwargs):
        return self.find(arguments, **kwargs).first

    def get(self, **kwargs):
        return self.client.get(self.service, **kwargs)

    def modify(self, json, **kwargs):
        return self.client.modify(self.service, json, **kwargs)

    def create(self, json, **kwargs):
        return self.client.create(self.service, json, **kwargs)

client = AppNexusClient()


def connect(username, password, debug=None, test=None):
    return client.connect(username, password, debug, test)


def find(service, arguments=None, representation=None, **kwargs):
    return client.find(service, arguments, representation, **kwargs)

__all__ = ["AppNexusClient", "client", "connect", "find"]
