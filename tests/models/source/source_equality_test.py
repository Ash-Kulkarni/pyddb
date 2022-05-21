from pyddb import DDB, Source, NewSource, get_source_type_by_name, BaseURL
import pytest


async def get_test_source():
    ddb = DDB(url=BaseURL.sandbox)
    [source] = await ddb.get_sources(source_id="9eb7af5a-df12-42a6-b308-8d0cb5558e74")
    return source


@pytest.mark.asyncio
async def test_same_source_is_equal():
    source = await get_test_source()
    assert source == source


@pytest.mark.asyncio
async def test_different_source_is_not_equal():
    source = await get_test_source()
    ddb = DDB(url=BaseURL.sandbox)
    [other_source] = await ddb.get_sources(
        source_id="4fa7bf55-551f-4243-92b4-ff37857c0daf"
    )
    assert source != other_source


@pytest.mark.asyncio
async def test_source_is_equal_to_same_new_source():
    source = await get_test_source()
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Assumption",
        reference="Average standard chiller SEER",
    )
    assert source == new_source


@pytest.mark.asyncio
async def test_source_is_not_equal_to_different_new_source():
    source = await get_test_source()
    new_source = NewSource(
        source_type=get_source_type_by_name("Assumption"),
        title="Not Assumption",
        reference="Average standard chiller SEER",
    )
    assert source != new_source
