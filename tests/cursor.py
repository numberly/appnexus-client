import pytest

from appnexus import representations
from appnexus.client import AppNexusClient
from appnexus.cursor import Cursor

from .helpers import gen_random_collection


@pytest.fixture
def response_dict():
    return {
        "count": 2,
        "campaigns": [
            {
                "profile_id": 139571597,
                "id": 147550505,
                "short_name": "Test",
                "labels": [
                    "Testing"
                ]
            },
            {
                "profile_id": 138278404,
                "id": 93831575,
                "short_name": "Still Test",
                "labels": [
                    "Testing"
                ]
            }
        ],
        "start_element": 0,
        "num_elements": 2,
        "status": "OK"
    }


@pytest.fixture
def response_dict2():
    return {
        "count": 1,
        "campaigns": {
            "profile_id": 139571597,
            "id": 427550505,
            "short_name": "Test",
            "labels": [
                "Testing"
            ]
        },
        "start_element": 0,
        "num_elements": 1,
        "status": "OK"
    }


@pytest.fixture
def random_response_dict():
    return gen_random_collection(count=324)


@pytest.fixture
def cursor(mocker, response_dict):
    client = AppNexusClient("test", "test")
    mocker.patch.object(client, 'get')
    client.get.return_value = response_dict
    return Cursor(client, "campaign", representations.raw)


@pytest.fixture
def random_cursor(mocker, random_response_dict):
    client = AppNexusClient("test", "test")
    mocker.patch.object(client, "get")
    client.get.side_effect = random_response_dict
    return Cursor(client, "campaign", representations.raw)


def test_cursor_count(cursor, response_dict):
    assert cursor.count() == response_dict["count"]


def test_cursor_length(cursor, response_dict):
    assert len(cursor) == response_dict["count"]


def test_cursor_extract_data_list(cursor, response_dict):
    assert list(cursor) == response_dict["campaigns"]


def test_cursor_extract_data_dict(cursor, response_dict2):
    cursor.client.get.return_value = response_dict2
    assert list(cursor) == [response_dict2["campaigns"]]


def test_cursor_first_with_list(cursor, response_dict):
    assert cursor.first == response_dict["campaigns"][0]


def test_cursor_first_with_dict(cursor, response_dict2):
    cursor.client.get.return_value = response_dict2
    assert cursor.first == response_dict2["campaigns"]


def test_cursor_iterate_with_list(cursor, response_dict):
    cursor.client.get.return_value = response_dict
    for x, y in zip(cursor, response_dict["campaigns"]):
        assert x == y


def test_cursor_iterate_with_long_list(mocker, cursor, response_dict):
    response_dict["campaigns"] *= 50
    response_dict["count"] = 200
    second_response_dict = response_dict.copy()
    cursor.client.get.side_effect = [response_dict, second_response_dict]
    for x, y in zip(cursor, response_dict["campaigns"]):
        assert x == y


# The test is written with a for loop to exhaust the iterable
def test_cursor_iterate_with_dict(mocker, cursor, response_dict2):
    cursor.response = response_dict2
    cursor.client.get.return_value = response_dict2
    for x, y in zip(cursor, [response_dict2["campaigns"]]):
        assert x == y


def test_iterate_one_element(mocker, cursor, response_dict2):
    cursor.client.get.return_value = response_dict2
    assert len(list(cursor)) == 1


def test_cursor_iterate_incomplete_page(mocker, cursor, response_dict):
    response_dict["campaigns"] *= 20
    response_dict["count"] = 80
    second_response_dict = response_dict.copy()
    cursor.client.get.side_effect = [response_dict, second_response_dict]
    for x, y in zip(cursor, response_dict["campaigns"]):
        assert x == y


def test_cursor_without_client():
    with pytest.raises(RuntimeError):
        Cursor(None, None, None)


def test_cursor_getitem_with_list(cursor, response_dict):
    cursor.client.get.return_value = response_dict
    assert cursor[0] == response_dict["campaigns"][0]


def test_cursor_getitem_with_dict(cursor, response_dict2):
    cursor.client.get.return_value = response_dict2
    assert cursor[0] == response_dict2["campaigns"]


def test_clone_iterate(cursor):
    assert list(cursor) == list(cursor.clone())


def test_uncallable_representation():
    with pytest.raises(TypeError):
        Cursor("dumb", "dumb", 42)


def test_requests_volume_on_iteration(cursor):
    _ = [r for r in cursor]
    assert cursor.client.get.call_count == 1
