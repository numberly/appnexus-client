from datetime import datetime
import functools
import logging
import time
import os

import requests

from appnexus.cursor import Cursor
from appnexus.exceptions import (AppNexusException, BadCredentials,
                                 NoAuth, RateExceeded)
from appnexus.utils import normalize_service_name

try:
    from configparser import ConfigParser
except ImportError:  # pragma: nocover
    from ConfigParser import ConfigParser

logger = logging.getLogger("appnexus-client")


class AppNexusClient(object):
    """Represents an active connection to the AppNexus API"""
    url = "https://api.appnexus.com/"
    test_url = "https://api-test.appnexus.com/"
    error_codes = {"RATE_EXCEEDED": RateExceeded}
    error_ids = {"NOAUTH": NoAuth}

    def __init__(self, username=None, password=None, test=False,
                 representation=None, token_file=None):
        self.credentials = {"username": username, "password": password}
        self.private_key = None
        self.token_handler = self.credentials_token_handler
        self.token = None
        self.token_file = None
        self.load_token(token_file)
        self.representation = representation
        self.test = bool(test)
        self._current_user = None
        self._generate_services()

    def _prepare_uri(self, service, **parameters):
        """Prepare the URI for a request

        :param service: The target service
        :type service: str
        :param kwargs: query parameters
        :return: The uri of the request
        """
        query_parameters = []
        for key, value in parameters.items():
            if isinstance(value, (list, tuple)):
                value = ",".join([str(member) for member in value])
            if isinstance(value, bool):
                value = "true" if value else "false"
            query_parameters.append("{}={}".format(key, value))

        if query_parameters:
            query_parameters = "&".join(query_parameters)
            uri = "{}{}?{}".format(self.base_url, service, query_parameters)
        else:
            uri = "{}{}".format(self.base_url, service)
        return uri

    # shiro: Coverage is disabled for this function because it's mocked and it
    # doesn't need testing (for the moment) since it's a simple instruction
    def _handle_rate_exceeded(self, response):  # pragma: no cover
        """Handles rate exceeded errors"""
        waiting_time = int(response.headers.get("Retry-After", 10))
        time.sleep(waiting_time)

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
            logger.debug(' '.join(map(str, (headers, uri, data))))

            response = send_method(uri, headers=headers, json=data)
            content_type = response.headers["Content-Type"].split(";")[0]

            if content_type == "application/json":
                response_data = response.json()
            else:
                return response.content

            try:
                self.check_errors(response, response_data["response"])
            except RateExceeded:
                self._handle_rate_exceeded(response)
            except NoAuth:
                self.update_token()
            else:
                valid_response = True
        if raw:
            return response_data
        return response_data["response"]

    def connect_from_key(self, username, key_name, private_key_filename):
        with open(private_key_filename, 'r') as f:
            self.private_key = {
                "username": username,
                "key_name": key_name,
                "private_key": f.read(),
            }
            self.token_handler = self.jwt_token_handler

    def jwt_token_handler(self):
        if self.private_key is None or None in self.private_key.values():
            raise RuntimeError("You must provide an username, "
                               "a key_name and a private_key path")
        from jwt import encode as jwt_encode
        jwt_payload = {
            "sub": self.private_key.get("username"),
            "iat": datetime.utcnow()
        }
        jwt_headers = {
            "kid": self.private_key.get("key_name"),
            "alg": "RS256",
            "typ": "JWT",
        }
        jwt_signature = jwt_encode(jwt_payload,
                                   self.private_key.get("private_key"),
                                   algorithm="RS256",
                                   headers=jwt_headers)
        response = requests.post(self.base_url + "v2/auth/jwt",
                             headers={"Content-Type": "text/plain"},
                             data=jwt_signature.decode())
        return response.json()["response"]

    def credentials_token_handler(self):
        if None in self.credentials.values():
            raise RuntimeError("You must provide an username and a password")
        credentials = dict(auth=self.credentials)
        url = self.test_url if self.test else self.url
        response = requests.post(url + "auth",
                                 json=credentials)
        return response.json()["response"]

    def update_token(self):
        """Request a new token and store it for future use"""
        logger.info('updating token')
        data = self.token_handler()
        print(data)
        if "error_id" in data and data["error_id"] == "NOAUTH":
            raise BadCredentials()
        if "error_code" in data and data["error_code"] == "RATE_EXCEEDED":
            time.sleep(150)
            return
        if "error_code" in data or "error_id" in data:
            raise AppNexusException(response)
        self.token = data["token"]
        self.save_token()
        return self.token

    def check_errors(self, response, data):
        """Check for errors and raise an appropriate error if needed"""
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
        """Retrieve data from AppNexus API"""
        return self._send(requests.get, service, **kwargs)

    def modify(self, service, json, **kwargs):
        """Modify an AppNexus object"""
        return self._send(requests.put, service, json, **kwargs)

    def create(self, service, json, **kwargs):
        """Create a new AppNexus object"""
        return self._send(requests.post, service, json, **kwargs)

    def delete(self, service, *ids, **kwargs):
        """Delete an AppNexus object"""
        return self._send(requests.delete, service, id=ids, **kwargs)

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

    def connect(self, username, password, test=None, representation=None,
                token_file=None):
        self.credentials = {"username": username, "password": password}
        if test is not None:
            self.test = bool(test)
        if representation is not None:
            self.representation = representation
        if token_file is not None:
            self.load_token(token_file)

    def connect_from_file(self, filename):
        config = ConfigParser()
        config.read(filename)
        connect_data = dict(config["appnexus"])
        self.connect(**connect_data)

    def _generate_services(self):
        for service in services_list:
            normalized_name = normalize_service_name(service)
            snake_name = normalized_name.replace('-', '_')
            generated_service = Service(self, normalized_name)
            setattr(self, snake_name, generated_service)

    def save_token(self):
        if not self.token_file or not self.token:
            return
        with open(self.token_file, mode='w') as fp:
            fp.write(self.token)

    def load_token(self, token_file=None):
        if not self.token_file:
            if not token_file:
                return
            self.token_file = token_file
        if not os.path.exists(self.token_file):
            return
        with open(self.token_file) as fp:
            self.token = fp.read().strip()

    def register_public_key(self, key_name, public_key_filename,
                            activate_key=True):
        from appnexus import PublicKey
        public_keys = PublicKey.find(user_id=self.current_user.id)
        if public_keys:
            for public_key in public_keys:
                if public_key.name == key_name:
                    return public_key
        with open(public_key_filename, 'r') as f:
            payload = {
                "active": activate_key,
                "name": key_name,
                "user_id": self.current_user.id,
                "encoded_value": f.read(),
            }
            return PublicKey.create(payload, user_id=self.current_user.id)

    @property
    def base_url(self):
        if self.test:
            return self.test_url
        else:
            return self.url

    @property
    def current_user(self):
        if self._current_user is None:
            from appnexus import User
            self._current_user = User.find_one(current=True)
        return self._current_user


services_list = ["AccountRecovery", "AdProfile", "Advertiser", "AdQualityRule",
                 "AdServer", "BatchSegment", "Brand", "Broker", "Browser",
                 "Campaign", "Carrier", "Category", "City", "ContentCategory",
                 "Country", "Creative", "CreativeFormat", "Currency",
                 "CustomModel", "CustomModelParser", "Deal", "DealBuyerAccess",
                 "DealFromPackage", "DemographicArea", "DeviceMake",
                 "DeviceModel", "DomainAuditStatus", "DomainList",
                 "ExternalInvCode", "InsertionOrder", "InventoryAttribute",
                 "InventoryResold", "IpRangeList", "Label", "Language",
                 "LineItem", "Lookup", "NativeCustomKey", "ManualOfferRanking",
                 "MediaSubtype", "MediaType", "Member", "MobileApp",
                 "MemberProfile", "ObjectLimit", "OperatingSystem",
                 "MobileAppInstance", "MobileAppInstanceList", "MobileAppStore",
                 "OperatingSystemExtended", "OperatingSystemFamily",
                 "OptimizationZone", "Package", "PackageBuyerAccess",
                 "PaymentRule", "Pixel", "Placement", "PlatformMember",
                 "PostalCode", "Profile", "ProfileSummary", "Publisher", "PublicKey",
                 "Region", "ReportStatus", "Search", "Segment", "Site",
                 "TechnicalAttribute", "Template", "ThirdpartyPixel", "User",
                 "UsergroupPattern", "VisibilityProfile", "Report"]


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

    def delete(self, *args):
        return self.client.delete(self.service, *args)


client = AppNexusClient()


@functools.wraps(client.connect)
def connect(*args, **kwargs):
    return client.connect(*args, **kwargs)


@functools.wraps(client.connect_from_file)
def connect_from_file(*args, **kwargs):
    return client.connect_from_file(*args, **kwargs)


@functools.wraps(client.find)
def find(*args, **kwargs):
    return client.find(*args, **kwargs)


__all__ = ["AppNexusClient", "client", "connect", "find"]
