import pytest

from appnexus.client import AppNexusClient
from appnexus import Campaign, Profile


@pytest.fixture
def campaign():
    Campaign.client = AppNexusClient("test", "test")
    return Campaign({
        "id": 9347201,
        "profile_id": 394828
    })


def test_campaign_profile(campaign, mocker):
    mocker.patch.object(Profile, "find_one")
    campaign.profile
    args, kwargs = Profile.find_one.call_args
    assert "id" in kwargs and kwargs["id"] == campaign.profile_id
