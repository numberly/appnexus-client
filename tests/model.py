# -*- coding:utf-8-*-

import pytest

from appnexus.client import AppNexusClient
from appnexus.cursor import Cursor
from appnexus.model import Model

Model.client = AppNexusClient("Test.", "dumb")


class Campaign(Model):
    service = "campaign"


@pytest.fixture
def response():
    return {
        "profile": [{
            "id": 21975591,
            "another_field": "another_value"
        }],
        "count": 8
    }


@pytest.fixture
def response2():
    return {
        "member": {
            "id": 395858219,
            "field": "value"
        },
        "count": 1
    }


def test_model_init_by_dict():
    x = Campaign({"id": 42})
    assert x.id == 42


def test_model_init_by_kwargs():
    x = Campaign(id=42)
    assert x.id == 42


def test_model_can_have_class_and_instance_client():
    Model.client = AppNexusClient('dumb', 'test')
    x = Campaign()
    x.client = AppNexusClient('dumbo', 'elephant')
    assert Campaign.client is not x.client


def test_model_find_returns_cursor(mocker, response):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response
    assert isinstance(Campaign.find(), Cursor)


def test_model_find_one_returns_model_instance(mocker, response2):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response2
    assert isinstance(Campaign.find_one(), Campaign)


def test_model_count(mocker, response):
    mocker.patch.object(Campaign.client, 'get')
    Campaign.client.get.return_value = response
    assert Campaign.count(id=21975591) == response["count"]


def test_model_save_missing_id(mocker):
    mocker.patch.object(Campaign.client, 'create')
    Campaign().save()
    assert Campaign.client.create.called


def test_model_save_with_id(mocker):
    mocker.patch.object(Campaign.client, 'modify')
    x = Campaign(id=42)
    x.attr = True
    x.save()
    assert Campaign.client.modify.called


def test_meta_call_client_meta(mocker):
    mocker.patch.object(Campaign.client, 'meta')
    Campaign.meta()
    assert Campaign.client.meta.called


def test_guess_service_name():
    class Test(Model):
        pass
    assert Test.service == "test"


def test_guess_composed_service_name():
    class TestService(Model):
        pass
    assert TestService.service == "test-service"


def test_setitem():
    x = Campaign(field=1)
    x.field = 42
    assert x.field == 42
    x.new_field = 23
    assert x.new_field == 23


def test_string_representation():
    x = Campaign(id=21)
    assert "21" in str(x)
    assert x.service in str(x).lower()


def test_service_can_override():
    class Test(Model):
        _service = "notatest"
    assert Test.service == "notatest"


def test_connect():
    x = Campaign()
    credentials = {"username": "dumb-user", "password": "dumb-password"}
    x.connect(**credentials)
    assert x.client


def test_create(mocker):
    mocker.patch.object(Campaign.client, "create")
    Campaign.create({"field": 42})
    assert Campaign.client.create.called


def test_modify(mocker):
    mocker.patch.object(Campaign.client, "modify")
    Campaign.modify({"field": 42})
    assert Campaign.client.modify.called
