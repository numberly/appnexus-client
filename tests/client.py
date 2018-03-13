# -*- coding:utf-8-*-
import time

import pytest
import requests

from appnexus.client import AppNexusClient
from appnexus.exceptions import AppNexusException, BadCredentials, NoAuth


@pytest.fixture
def username():
    return "test"


@pytest.fixture
def password():
    return "passtest"


@pytest.fixture
def credentials(username, password):
    credentials = dict(username=username, password=password)
    return dict(auth=credentials)


@pytest.fixture
def client(username, password):
    return AppNexusClient(username, password)


@pytest.fixture
def token():
    return "test_token"


@pytest.fixture
def connected_client(client, token):
    client.token = token
    return client


def test_connect_send_credentials(mocker, client, credentials):
    mocker.patch("requests.post")
    client.update_token()
    args, kwargs = requests.post.call_args
    assert "json" in kwargs and kwargs["json"] == credentials


def test_connect_store_token(mocker, client, token):
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response": {"token": token}}
    client.update_token()
    assert hasattr(client, "token") and client.token == token


def test_connect_bad_credentials(mocker, client):
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response": {"error_id": "NOAUTH"}}
    with pytest.raises(BadCredentials):
        client.update_token()


def test_connect_exception(mocker, client):
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response": {"error_id": "WHATEVER"}}
    with pytest.raises(AppNexusException):
        client.update_token()


def test_uri_service(client):
    assert client._prepare_uri("service") == client.url + "service"


def test_uri_query_parameters(client):
    uri = client._prepare_uri("service", id=42, the="game")
    expected_uris = [client.url + "service?id=42&the=game",
                     client.url + "service?the=game&id=42"]
    assert uri in expected_uris


def test_uri_list_parameter(client):
    uri = client._prepare_uri("service", id=[1, 2, 3])
    expected_uri = client.url + "service?id=1,2,3"
    assert uri == expected_uri


def test_headers_token(mocker, connected_client, token):
    mocker.patch.object(requests, "get")
    connected_client.get("campaign")
    args, kwargs = requests.get.call_args
    headers = kwargs["headers"]
    assert "Authorization" in headers and headers["Authorization"] == token


def test_check_errors_noauth(mocker, client):
    response = mocker.MagicMock()
    response_dict = {"response": {"error_id": "NOAUTH"}}
    response.json.return_value = response_dict
    with pytest.raises(NoAuth):
        client.check_errors(response, response_dict["response"])


def test_send_success(mocker, connected_client):
    mocker.patch("requests.get")
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    requests.get().json.return_value = {"response": {"campaign": {}}}
    response = connected_client._send(requests.get, "campaign", id=3)
    assert "campaign" in response


def test_send_reconnect(mocker, connected_client):
    mocker.patch("requests.get")
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response": {"token": token}}
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    requests.get().json.side_effect = [{"response": {"error_id": "NOAUTH"}},
                                       {"response": {"campaign": {}}}]
    response = connected_client._send(requests.get, "campaign", id=3)
    assert requests.post().json.call_count == 1
    assert "campaign" in response


def test_send_handle_rate_exceeded(mocker, connected_client):
    mocker.patch("requests.get")
    mocker.patch.object(connected_client, "_handle_rate_exceeded")
    requests.get().json.side_effect = [
        {"response": {"error_code": "RATE_EXCEEDED"}},
        {"response": {"campaign": {}}}
    ]
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    connected_client._send(requests.get, "campaign", id=3)
    assert connected_client._handle_rate_exceeded.called


def test_send_unknown_error(mocker, connected_client):
    mocker.patch("requests.get")
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    requests.get().json.return_value = {"response": {"error_id": "WHATEVER"}}
    with pytest.raises(AppNexusException):
        connected_client._send(requests.get, "campaign", id=3)


def test_send_method_send_json(mocker, connected_client):
    mocker.patch.object(requests, "post")
    data = dict(field="value")
    connected_client._send(requests.post, "campaign", data)
    args, kwargs = requests.post.call_args
    assert "json" in kwargs and kwargs["json"] == data


def test_send_raw(mocker, connected_client):
    mocker.patch("requests.get")
    requests.get().json.return_value = {"response": {"campaign": {}}}
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    response = connected_client._send(requests.get, "campaign", id=3, raw=True)
    assert "response" in response


def test_get_return_dict(mocker, connected_client):
    mocker.patch("requests.get")
    requests.get().json.return_value = {"response": {"campaign": {}}}
    requests.get.return_value.headers = {'Content-Type': 'application/json'}
    cursor = connected_client.get("campaign")
    assert isinstance(cursor, dict)


def test_modify_return_dict(mocker, connected_client):
    mocker.patch("requests.put")
    requests.put().json.return_value = {"response": {"campaign": {}}}
    requests.put.return_value.headers = {'Content-Type': 'application/json'}
    cursor = connected_client.modify("campaign", None)
    assert isinstance(cursor, dict)


def test_modify_send_json(mocker, connected_client):
    mocker.patch.object(requests, "put")
    data = dict(field="value")
    connected_client.modify("campaign", data)
    args, kwargs = requests.put.call_args
    assert "json" in kwargs and kwargs["json"] == data


def test_create_return_dict(mocker, connected_client):
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response": {"campaign": {}}}
    requests.post.return_value.headers = {'Content-Type': 'application/json'}
    cursor = connected_client.create("campaign", None)
    assert isinstance(cursor, dict)


def test_create_send_json(mocker, connected_client):
    mocker.patch.object(requests, "post")
    data = dict(field="value")
    connected_client.create("campaign", data)
    args, kwargs = requests.post.call_args
    assert "json" in kwargs and kwargs["json"] == data


def test_delete_return_dict(mocker, connected_client):
    mocker.patch("requests.delete")
    requests.delete().json.return_value = {"response": {"campaign": {}}}
    requests.delete.return_value.headers = {'Content-Type': 'application/json'}
    cursor = connected_client.delete("campaign", 42)
    assert isinstance(cursor, dict)


def test_delete_send_ids(mocker, connected_client):
    mocker.patch.object(requests, "delete")
    mocker.patch.object(connected_client, "_prepare_uri")
    ids = [1, 2, 3]
    connected_client.delete("campaign", *ids)
    args, parameters = connected_client._prepare_uri.call_args
    assert "id" in parameters and list(parameters["id"]) == ids


def test_append_return_dict(mocker, connected_client):
    mocker.patch("requests.put")
    requests.put().json.return_value = {"response": {"campaign": {}}}
    requests.put.return_value.headers = {'Content-Type': 'application/json'}
    cursor = connected_client.append("campaign", None)
    assert isinstance(cursor, dict)


def test_append_query_param_append(mocker, connected_client):
    mocker.patch.object(connected_client, "_send")
    connected_client.append("campaign", None)
    args, kwargs = connected_client._send.call_args
    assert "append" in kwargs and kwargs["append"]


def test_meta_call_meta_endpoint(mocker, connected_client):
    mocker.patch.object(connected_client, "_send")
    connected_client.meta("campaign")
    args, kwargs = connected_client._send.call_args
    assert args[1].endswith("/meta")


def test_sleep_when_rate_exceeded_on_auth(mocker, connected_client):
    mocker.patch("requests.post")
    requests.post().json.return_value = {"response":
                                         {"error_code": "RATE_EXCEEDED"}}
    mocker.patch("time.sleep")
    connected_client.update_token()
    assert time.sleep.called


def test_without_credentials():
    client = AppNexusClient()
    with pytest.raises(RuntimeError):
        client.update_token()


def test_connect(mocker):
    mocker.patch.object(requests, "post")
    requests.post().json.return_value = {"response": {"token": "TOKEN"}}
    client = AppNexusClient()
    credentials = {"username": "appnexususer", "password": "my-password"}
    client.connect(**credentials)
    client.update_token()
    _, kwargs = requests.post.call_args
    assert kwargs["json"] == {"auth": credentials}


def test_service_find(mocker, connected_client):
    mocker.patch.object(connected_client, "find")
    connected_client.creative.find()
    assert connected_client.find.called


def test_service_find_one(mocker, connected_client):
    mocker.patch.object(connected_client, "find")
    connected_client.creative.find_one()
    assert connected_client.find.called


def test_service_get(mocker, connected_client):
    mocker.patch.object(connected_client, "get")
    connected_client.creative.get()
    assert connected_client.get.called


def test_service_modify(mocker, connected_client):
    mocker.patch.object(connected_client, "modify")
    connected_client.creative.modify(json={})
    assert connected_client.modify.called


def test_service_create(mocker, connected_client):
    mocker.patch.object(connected_client, "create")
    connected_client.creative.create(json={})
    assert connected_client.create.called


def test_global_client_connect(mocker):
    from appnexus import client, connect
    mocker.patch.object(client, "connect")
    credentials = {"username": "appnexususer", "password": "my-password"}
    connect(**credentials)
    assert client.connect.called


def test_global_client_find(mocker):
    from appnexus import client, find
    mocker.patch.object(client, "find")
    find("creative")
    assert client.find.called
