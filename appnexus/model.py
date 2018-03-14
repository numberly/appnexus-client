import logging
import re
import time

from thingy import Thingy

from appnexus.client import AppNexusClient, client, services_list
from appnexus.utils import classproperty, normalize_service_name

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
    def delete(cls, *args, **kwargs):
        return cls.client.delete(cls.service, *args, **kwargs)

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
        return type(self)(result)


class Campaign(Model):

    @property
    def profile(self):
        return Profile.find_one(id=self.profile_id)


class Report(Model):

    def download(self, retry_count=3, **kwargs):
        # Check if the report is ready to download
        while self.is_ready() != 'ready' and retry_count > 0:
            retry_count -= 1
            time.sleep(1)

        return self.client.get("report-download", id=self.report_id)

    def is_ready(self):
        return self.client.get('report', id=self.report_id)['execution_status']


def create_models(services_list):
    for service in services_list:
        model = type(service, (Model,), {})
        globals().setdefault(service, model)


create_models(services_list)

__all__ = ["Model", "services_list"] + services_list
