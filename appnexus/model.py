import logging
import re

from thingy import Thingy

from appnexus.utils import classproperty, normalize_service_name
from appnexus.client import client, services_list, AppNexusClient

logger = logging.getLogger("appnexus-client")


class Model(Thingy):
    """Generic model for AppNexus data"""
    _service = None
    client = client
    service_name_re = re.compile("([A-Z][a-z]*)")

    @classmethod
    def connect(cls, username, password):
        cls.client = AppNexusClient(username, password)
        return cls.client

    @classmethod
    def find(cls, **kwargs):
        return cls.client.find(cls.service, representation=cls.constructor,
                               **kwargs)

    @classmethod
    def find_one(cls, **kwargs):
        return cls.find(**kwargs).first

    @classmethod
    def count(cls, **kwargs):
        return cls.find(**kwargs).count()

    @classmethod
    def meta(cls):
        return cls.client.meta(cls.service)

    @classproperty
    def envelope(cls):
        return cls.service

    @classproperty
    def service(cls):
        if cls._service is None:
            cls._service = normalize_service_name(cls.__name__)
        return cls._service

    @classmethod
    def create(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.create(cls.service, payload, **kwargs)

    @classmethod
    def delete(cls, *args):
        return cls.client.delete(cls.service, *args)

    @classmethod
    def modify(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.modify(cls.service, payload, **kwargs)

    @classmethod
    def constructor(cls, client, service, obj):
        cls.client = client
        cls._service = service
        return cls(obj)

    def save(self, **kwargs):
        payload = self.__dict__
        if "id" not in self.__dict__:
            logger.info("creating a {}".format(self.service))
            result = self.create(payload, **kwargs)
        else:
            result = self.modify(payload, id=self.id, **kwargs)
        return result


class Campaign(Model):

    @property
    def profile(self):
        return Profile.find_one(id=self.profile_id)


class CustomModel(Model):

    @classproperty
    def envelope(cls):
        return cls.service.replace('-', '_')


def gen_services(services_list):
    for service in services_list:
        model = type(service, (Model,), {})
        globals().setdefault(service, model)


gen_services(services_list)

__all__ = ["Model", "services_list"] + services_list
