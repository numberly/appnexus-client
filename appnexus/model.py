import logging
import re
import time

from thingy import Thingy

from appnexus.client import AppNexusClient, client, services_list
from appnexus.utils import classproperty, normalize_service_name

logger = logging.getLogger("appnexus-client")


class Model(Thingy):
    """Generic model for AppNexus data"""
    client = client
    _service_name = None
    service_name_re = re.compile("([A-Z][a-z]*)")

    @classmethod
    def connect(cls, username, password):
        cls.client = AppNexusClient(username, password)
        return cls.client

    @classmethod
    def find(cls, **kwargs):
        representation = (kwargs.pop("representation", None)
                          or cls.client.representation
                          or cls.constructor)
        return cls.client.find(cls.service_name, representation=representation,
                               **kwargs)

    @classmethod
    def find_one(cls, **kwargs):
        return cls.find(**kwargs).first

    @classmethod
    def count(cls, **kwargs):
        return cls.find(**kwargs).count()

    @classmethod
    def meta(cls):
        return cls.client.meta(cls.service_name)

    @classproperty
    def envelope(cls):
        return cls.service_name

    @classproperty
    def service_name(cls):
        if cls._service_name is None:
            cls._service_name = normalize_service_name(cls.__name__)
        return cls._service_name

    @classmethod
    def create(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.create(cls.service_name, payload, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs):
        return cls.client.delete(cls.service_name, *args, **kwargs)

    @classmethod
    def modify(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.modify(cls.service_name, payload, **kwargs)

    @classmethod
    def constructor(cls, client, service_name, obj):
        cls.client = client
        cls._service_name = service_name
        return cls(obj)

    def save(self, **kwargs):
        payload = self.__dict__
        if "id" not in self.__dict__:
            logger.info("creating a {}".format(self.service_name))
            result = self.create(payload, **kwargs)
        else:
            result = self.modify(payload, id=self.id, **kwargs)

        self.update(result)
        return self


class Report(Model):

    def download(self, retry_count=3, **kwargs):
        # Check if the report is ready to download
        while self.is_ready() != "ready" and retry_count > 0:
            logger.debug("Report not ready yet; retrying again")
            retry_count -= 1
            time.sleep(1)

        return self.client.get("report-download", id=self.report_id)

    def is_ready(self):
        return self.client.get("report", id=self.report_id)["execution_status"]


class ChangeLogMixin():

    @property
    def changelog(self, **kwargs):
        kwargs.setdefault("service", self.service_name)
        kwargs.setdefault("resource_id", self.id)
        return ChangeLog.find(**kwargs)


class ProfileMixin():

    @property
    def profile(self):
        return Profile.find_one(id=self.profile_id)


def create_models(services_list):
    for service_name in services_list:
        ancestors = [Model]
        if service_name in ("Campaign", "InsertionOrder", "LineItem",
                            "Profile"):
            ancestors.append(ChangeLogMixin)
        if service_name in ("AdQualityRule", "Advertiser", "Campaign",
                            "Creative", "LineItem", "PaymentRule"):
            ancestors.append(ProfileMixin)
        model = type(service_name, tuple(ancestors), {})
        globals().setdefault(service_name, model)


create_models(services_list)

__all__ = ["Model", "services_list"] + services_list
