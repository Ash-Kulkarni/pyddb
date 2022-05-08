from pyddb_client import DDB, SourceType
import pytest

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_source_types():
    response = await ddb.get_source_types()
    assert isinstance(response, list)
    assert isinstance(response[0], SourceType)
