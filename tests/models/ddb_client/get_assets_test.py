from pyddb import DDB, Asset
import pytest

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_assets():
    response = await ddb.get_assets()
    assert isinstance(response, list)
    assert isinstance(response[0], Asset)
