from pyddb.models import DDB, Source, NewSource
from pyddb.utils import get_source_type_by_name
import pytest


async def get_test_source():
    ddb = DDB()
    [source] = await ddb.get_sources(source_id="9eb7af5a-df12-42a6-b308-8d0cb5558e74")
    return source


@pytest.mark.asyncio
async def test_same_new_source_is_equal():
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Assumption",
        reference="Average standard chiller SEER",
    )
    assert new_source == new_source


@pytest.mark.asyncio
async def test_different_new_source_is_not_equal():
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Assumption",
        reference="Average standard chiller SEER",
    )
    other_new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Not Assumption",
        reference="Average standard chiller SEER",
    )
    assert new_source != other_new_source


@pytest.mark.asyncio
async def test_new_source_is_equal_to_same_source():
    source = await get_test_source()
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Assumption",
        reference="Average standard chiller SEER",
    )
    assert new_source == source


@pytest.mark.asyncio
async def test_new_source_is_not_equal_to_different_source():
    source = await get_test_source()
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Not Assumption",
        reference="Average standard chiller SEER",
    )
    assert new_source != source
