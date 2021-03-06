from pyddb import (
    DDB,
    NewParameter,
    NewRevision,
    get_parameter_type_by_name,
    get_unit_by_name,
    BaseURL,
)
import pytest


async def get_test_parameter():
    ddb = DDB(url=BaseURL.sandbox)
    [parameter] = await ddb.get_parameters(
        parameter_id="41be6903-662f-429f-a108-92f8f3d91db4"
    )
    return parameter, parameter.revision


@pytest.mark.asyncio
async def test_same_parameter_is_equal():
    parameter, _ = await get_test_parameter()
    assert parameter == parameter


@pytest.mark.asyncio
async def test_different_parameter_is_not_equal():
    parameter, _ = await get_test_parameter()
    ddb = DDB(url=BaseURL.sandbox)
    [other_parameter] = await ddb.get_parameters(
        parameter_id="19d3f1da-2b30-4f61-a9b7-a2e3b0ac9a48"
    )
    assert parameter != other_parameter


@pytest.mark.asyncio
async def test_parameter_is_equal_to_same_new_parameter():

    parameter, revision = await get_test_parameter()
    new_revision = NewRevision(
        value=123, unit=get_unit_by_name("m"), source=revision.source
    )

    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"), revision=new_revision
    )
    assert parameter == new_parameter


@pytest.mark.asyncio
async def test_parameter_is_not_equal_to_different_new_parameter():
    parameter, revision = await get_test_parameter()
    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"),
        revision=NewRevision(
            value=124, unit=get_unit_by_name("m"), source=revision.source
        ),
    )
    assert parameter != new_parameter
