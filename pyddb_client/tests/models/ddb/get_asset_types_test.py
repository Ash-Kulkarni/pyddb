from pyddb_client import DDB, AssetType
import pytest

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_asset_types():
    response = await ddb.get_asset_types()
    assert isinstance(response, list)
    assert isinstance(response[0], AssetType)
