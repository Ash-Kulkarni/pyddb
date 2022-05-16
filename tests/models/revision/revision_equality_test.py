from pyddb import DDB, NewRevision, get_unit_by_name
import pytest


async def get_test_revision():
    ddb = DDB()
    [parameter] = await ddb.get_parameters(
        parameter_id="41be6903-662f-429f-a108-92f8f3d91db4"
    )
    return parameter.revision, parameter.revision.source


@pytest.mark.asyncio
async def test_same_revision_is_equal():
    revision, _ = await get_test_revision()
    assert revision == revision


# the revision is always a string
# the new revision may not always match if there is a float/int data mismatch
@pytest.mark.asyncio
async def test_revision_is_equal_to_same_new_revision():
    revision, source = await get_test_revision()
    new_revision = NewRevision(value=123.0, unit=get_unit_by_name("m"), source=source)
    assert revision == new_revision


@pytest.mark.asyncio
async def test_revision_is_not_equal_to_different_new_revision():
    revision, source = await get_test_revision()
    new_revision = NewRevision(value=124, unit=get_unit_by_name("m"), source=source)
    assert revision != new_revision
