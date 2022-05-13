from pyddb.models import DDB, Source, NewSource, Parameter, NewParameter
from pyddb.utils import get_source_type_by_name
import pytest


async def get_test_source():
    ddb = DDB()
    [parameter] = await ddb.get_parameters(
        parameter_id="41be6903-662f-429f-a108-92f8f3d91db4"
    )
    return parameter


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
