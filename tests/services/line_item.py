import pytest

from appnexus import BudgetSplitter, LineItem
from appnexus.client import AppNexusClient


@pytest.fixture
def line_item():
    LineItem.client = AppNexusClient("test", "test")
    return LineItem({
        "id": 42
    })


def test_line_item_budget_splitter(line_item, mocker):
    mocker.patch.object(BudgetSplitter, "find_one")
    line_item.budget_splitter
    args, kwargs = BudgetSplitter.find_one.call_args
    assert "id" in kwargs and kwargs["id"] == line_item.id
