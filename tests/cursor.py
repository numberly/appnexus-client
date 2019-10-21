import pytest

from appnexus import representations
from appnexus.client import AppNexusClient
from appnexus.cursor import Cursor

from .helpers import gen_ordered_collection, gen_random_collection

COLLECTION_SIZE = 324


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
    return gen_random_collection(count=COLLECTION_SIZE)


@pytest.fixture
def ordered_response_dict():
    return gen_ordered_collection(start_element=0, count=COLLECTION_SIZE)


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


@pytest.fixture
def ordered_cursor(mocker, ordered_response_dict):
    client = AppNexusClient("test", "test")
    mocker.patch.object(client, "get")
    client.get.side_effect = ordered_response_dict
    return Cursor(client, "campaign", representations.raw)


def mock_ordered_cursor(mocker, start=0, count=COLLECTION_SIZE, factor=1):
    client = AppNexusClient("test", "test")
    mocker.patch.object(client, "get")
    client.get.side_effect = gen_ordered_collection(start, count) * factor
    cursor = Cursor(client, "campaign", representations.raw)
    mocker.patch.object(cursor, "get_page", wraps=cursor.get_page)
    return cursor


@pytest.fixture
def double_ordered_cursor(mocker, ordered_response_dict):
    client = AppNexusClient("test", "test")
    mocker.patch.object(client, "get")
    client.get.side_effect = ordered_response_dict * 2
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


def test_skip_none(mocker):
    cursor = mock_ordered_cursor(mocker, start=0, count=COLLECTION_SIZE)
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE
    assert results[0]['id'] == 0
    assert results[-1]['id'] == COLLECTION_SIZE - 1
    assert cursor.get_page.call_count == 4


def test_skip_ten(mocker):
    skip = 10
    cursor = mock_ordered_cursor(mocker, start=skip, count=COLLECTION_SIZE)
    cursor.skip(skip)
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE - skip
    assert results[0]['id'] == skip
    assert results[-1]['id'] == COLLECTION_SIZE - 1
    assert cursor.get_page.call_count == 4


def test_skip_hundred_ten(mocker):
    skip = 110
    cursor = mock_ordered_cursor(mocker, start=skip, count=COLLECTION_SIZE)
    cursor.skip(skip)
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE - skip
    assert results[0]['id'] == skip
    assert results[-1]['id'] == COLLECTION_SIZE - 1
    assert cursor.get_page.call_count == 3


def test_skip_twice(mocker):
    skip = 10
    cursor = mock_ordered_cursor(mocker, start=skip, count=COLLECTION_SIZE,
                                 factor=2)
    cursor.skip(skip)
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE - skip
    assert results[0]['id'] == skip
    assert cursor.get_page.call_count == 4
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE - skip
    assert results[0]['id'] == skip
    assert cursor.get_page.call_count == 8


def test_limit_ten(mocker):
    limit = 10
    cursor = mock_ordered_cursor(mocker, start=0, count=limit)
    cursor.limit(limit)
    results = [r for r in cursor]
    assert len(results) == limit
    assert results[0]['id'] == 0
    assert results[-1]['id'] == limit - 1
    assert cursor.get_page.call_count == 1


def test_limit_hundred_ten(mocker):
    limit = 110
    cursor = mock_ordered_cursor(mocker, start=0, count=limit)
    cursor.limit(limit)
    results = [r for r in cursor]
    assert len(results) == limit
    assert results[0]['id'] == 0
    assert results[-1]['id'] == limit - 1
    assert cursor.get_page.call_count == 2


def test_limit_thousand(mocker):
    limit = 1000
    cursor = mock_ordered_cursor(mocker, start=0, count=COLLECTION_SIZE)
    cursor.limit(limit)
    results = [r for r in cursor]
    assert len(results) == COLLECTION_SIZE
    assert results[0]['id'] == 0
    assert results[-1]['id'] == COLLECTION_SIZE - 1
    assert cursor.get_page.call_count == 4


def test_limit_twice(mocker):
    limit = 50
    cursor = mock_ordered_cursor(mocker, start=0, count=limit, factor=2)
    cursor.limit(limit)
    results = [r for r in cursor]
    assert len(results) == limit
    assert results[0]['id'] == 0
    assert results[-1]['id'] == limit - 1
    assert cursor.get_page.call_count == 1
    results = [r for r in cursor]
    assert len(results) == limit
    assert results[0]['id'] == 0
    assert results[-1]['id'] == limit - 1
    assert cursor.get_page.call_count == 2


def test_skip_and_limit(mocker):
    skip = 10
    limit = 150
    cursor = mock_ordered_cursor(mocker, start=skip, count=skip + limit)
    cursor.skip(skip)
    cursor.limit(limit)
    results = [r for r in cursor]
    assert len(results) == limit
    assert results[0]['id'] == skip
    assert results[-1]['id'] == limit + skip - 1
    assert cursor.get_page.call_count == 2
