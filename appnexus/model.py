import logging
import time

from thingy import Thingy

from appnexus.client import AppNexusClient, client, services_list
from appnexus.utils import classproperty, normalize_service_name

logger = logging.getLogger("appnexus-client")


class Model(Thingy):
    """Generic model for AppNexus data"""
    _update_on_save = True
    client = client

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
    def service_name(cls):
        return normalize_service_name(cls.__name__)

    @classmethod
    def create(cls, payload, **kwargs):
        payload = {cls.service_name: payload}
        return cls.client.create(cls.service_name, payload, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs):
        return cls.client.delete(cls.service_name, *args, **kwargs)

    @classmethod
    def modify(cls, payload, **kwargs):
        payload = {cls.service_name: payload}
        return cls.client.modify(cls.service_name, payload, **kwargs)

    @classmethod
    def constructor(cls, client, service_name, obj):
        cls.client = client
        cls.service_name = service_name
        return cls(obj)

    def save(self, **kwargs):
        payload = self.__dict__
        if "id" not in self.__dict__:
            logger.info("creating a {}".format(self.service_name))
            result = self.create(payload, **kwargs)
        else:
            result = self.modify(payload, id=self.id, **kwargs)

        if self._update_on_save:
            self.update(result)
        return self


class AlphaModel(Model):
    _update_on_save = False
    _modifiable_fields = ()

    def __setattr__(self, attr, value):
        if self._modifiable_fields and attr not in self._modifiable_fields:
            super(AlphaModel, self).__setattr__(attr, value)
        raise AttributeError("'{}' can't be modified".format(attr))

    @classmethod
    def find(cls, **kwargs):
        raise NotImplemented("Can't get multiple objects on '{}' service"
                             .format(cls.service_name))

    @classmethod
    def find_one(cls, id, **kwargs):
        representation = (kwargs.pop("representation", None)
                          or cls.client.representation
                          or cls.constructor)
        response = cls.client.get(cls.service_name, id=id, **kwargs)
        if representation:
            return representation(cls.client, cls.service_name, response)
        return response

    @classmethod
    def modify(cls, payload, **kwargs):
        non_modifiable_fields = set(payload) - set(cls._modifiable_fields)
        for field in non_modifiable_fields:
            del payload[field]
        return super(AlphaModel, cls).modify(payload, **kwargs)


class CustomModelHash(AlphaModel):
    _modifiable_fields = ("coefficients",)


class CustomModelLogit(AlphaModel):
    pass


class CustomModelLUT(AlphaModel):
    _modifiable_fields = ("coefficients",)


class LineItemModel(AlphaModel):
    pass


class Report(Model):

    def download(self, retry_count=3, **kwargs):
        while not self.is_ready and retry_count > 0:
            retry_count -= 1
            time.sleep(1)
        return self.client.get("report-download", id=self.report_id)

    @property
    def is_ready(self):
        status = Report.find_one(id=self.report_id).execution_status
        return (status == "ready")


class ChangeLogMixin():

    @property
    def changelog(self):  # flake8: noqa: F821
        return ChangeLog.find(service=self.service_name, resource_id=self.id)


class ProfileMixin():

    @property
    def profile(self):  # flake8: noqa: F821
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
