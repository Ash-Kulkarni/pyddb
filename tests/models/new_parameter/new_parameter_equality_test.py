from webbrowser import get
from pyddb.models import DDB, NewParameter, NewRevision, Source, NewSource, BaseURL
from pyddb.utils import get_source_type_by_name, get_parameter_type_by_name
import pytest

from pyddb.utils.read_data import get_unit_by_name


async def get_test_parameter():
    ddb = DDB(url=BaseURL.sandbox)
    [parameter] = await ddb.get_parameters(
        parameter_id="41be6903-662f-429f-a108-92f8f3d91db4"
    )
    return parameter, parameter.revision


@pytest.mark.asyncio
async def test_same_new_parameter_is_equal():
    parameter, revision = await get_test_parameter()
    new_revision = NewRevision(
        value=123.0, unit=get_unit_by_name("m"), source=revision.source
    )

    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"), revision=new_revision
    )
    assert new_parameter == new_parameter


@pytest.mark.asyncio
async def test_different_new_parameter_is_not_equal():
    parameter, revision = await get_test_parameter()
    new_revision = NewRevision(
        value=123.0, unit=get_unit_by_name("m"), source=revision.source
    )

    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"), revision=new_revision
    )
    other_new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Building height restriction"),
        revision=new_revision,
    )
    assert new_parameter != other_new_parameter


@pytest.mark.asyncio
async def test_new_parameter_is_equal_to_same_parameter():

    parameter, revision = await get_test_parameter()

    new_revision = NewRevision(
        value=123, unit=get_unit_by_name("m"), source=revision.source
    )

    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"), revision=new_revision
    )
    assert new_parameter == parameter


@pytest.mark.asyncio
async def test_parameter_is_not_equal_to_different_new_parameter():
    parameter, revision = await get_test_parameter()
    new_parameter = NewParameter(
        parameter_type=get_parameter_type_by_name("Altitude"),
        revision=NewRevision(
            value=124.0, unit=get_unit_by_name("m"), source=revision.source
        ),
    )
    assert new_parameter != parameter
