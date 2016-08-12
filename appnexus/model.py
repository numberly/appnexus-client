# -*- coding:utf-8-*-

import re

from appnexus.utils import classproperty, normalize_service_name
from appnexus.client import client, services_list, AppNexusClient


class Model(object):
    """Generic model for AppNexus data"""

    _service = None
    client = client
    service_name_re = re.compile("([A-Z][a-z]*)")

    def __init__(self, dict_attr=None, **attrs):
        self.attrs = dict()
        if dict_attr is not None:
            self.attrs.update(dict_attr)
        self.attrs.update(attrs)
        self.last_saved_attrs = self.attrs.copy()

        self.delete = self._delete_instance

    def __getitem__(self, name):
        if name in self.attrs:
            return self.attrs[name]
        raise AttributeError

    def __setitem__(self, name, value):
        self.attrs[name] = value

    def __delitem__(self, name):
        if name in self.attrs:
            del self.attrs[name]

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def __str__(self):
        if "id" in self:
            return "<{} #{}>".format(self.service, self["id"])
        return "<{} not saved>".format(self.service)

    __repr__ = __str__

    def __contains__(self, name):
        return name in self.attrs

    def _generate_diff(self):
        diff = dict()
        for key, value in self.attrs.items():
            if (key not in self.last_saved_attrs or
                    self.last_saved_attrs[key] != value):
                diff[key] = value

        old_keys = set(self.last_saved_attrs)
        new_keys = set(self.attrs)
        only_old_keys = old_keys.difference(new_keys)
        for key in only_old_keys:
            diff[key] = None

        return diff

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

    def save(self, **kwargs):
        """Save the stored object on appnexus"""
        diff = self._generate_diff()
        if not diff and "id" in self:
            return
        payload = {self.envelope: diff}
        if "id" not in self:
            result = self.client.create(self.service, payload, **kwargs)
        else:
            result = self.client.modify(self.service, payload, id=self["id"],
                                        **kwargs)
        self.last_saved_attrs = self.attrs.copy()
        return result

    @classmethod
    def create(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.create(cls.service, payload, **kwargs)

    @classmethod
    def delete(cls, *args):
        return cls.client.delete(cls.service, *args)

    def _delete_instance(self):
        return self.client.delete(self.service, self["id"])

    @classmethod
    def modify(cls, payload, **kwargs):
        payload = {cls.envelope: payload}
        return cls.client.modify(cls.service, payload, **kwargs)

    @classmethod
    def constructor(cls, client, service, obj):
        cls.client = client
        cls._service = service
        return cls(obj)


class Campaign(Model):

    @property
    def profile(self):
        return Profile.find_one(id=self["profile_id"])


def gen_services(services_list):
    for service in services_list:
        model = type(service, (Model,), {})
        globals().setdefault(service, model)

gen_services(services_list)

__all__ = ["Model", "services_list"] + services_list
