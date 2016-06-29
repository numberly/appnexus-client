# -*- coding:utf-8-*-

import pytest

from appnexus.exceptions import AppNexusException, BadCredentials


@pytest.fixture
def appnexus_exception(mocker):
    response = mocker.MagicMock()
    response.json.return_value = {
        "response": {
            "error_code": "INVALID_LOGIN",
            "error": "You didn't provided credentials"
        }
    }
    return AppNexusException(response)


@pytest.fixture
def empty_appnexus_exception():
    return AppNexusException()


@pytest.fixture
def bad_credentials():
    return BadCredentials()


def test_appnexus_exception_str(appnexus_exception):
    assert "INVALID_LOGIN" in str(appnexus_exception)


def test_empty_appnexus_exception_str(empty_appnexus_exception):
    assert "Error" in str(empty_appnexus_exception)


def test_bad_credentials_str(bad_credentials):
    assert "bad credentials" in str(bad_credentials)
