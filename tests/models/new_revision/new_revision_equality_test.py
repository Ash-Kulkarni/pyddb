from pyddb.models import DDB, NewRevision
from pyddb.utils import get_unit_by_name
import pytest


async def get_test_revision():
    ddb = DDB()
    [parameter] = await ddb.get_parameters(
        parameter_id="41be6903-662f-429f-a108-92f8f3d91db4"
    )
    return parameter.revision, parameter.revision.source


@pytest.mark.asyncio
async def test_same_new_revision_is_equal():
    _, source = await get_test_revision()
    new_revision = NewRevision(value=123, unit=get_unit_by_name("m"), source=source)
    assert new_revision == new_revision


@pytest.mark.asyncio
async def test_new_revision_is_equal_to_same_revision():
    revision, source = await get_test_revision()
    new_revision = NewRevision(value=123.0, unit=get_unit_by_name("m"), source=source)
    assert new_revision == revision


@pytest.mark.asyncio
async def test_new_revision_is_not_equal_to_different_revision():
    revision, source = await get_test_revision()
    new_revision = NewRevision(value=124.0, unit=get_unit_by_name("m"), source=source)
    assert new_revision != revision
