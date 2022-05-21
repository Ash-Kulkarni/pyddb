from pyddb import DDB, Asset, BaseURL
import pytest

ddb = DDB(url=BaseURL.sandbox)


@pytest.mark.asyncio
async def test_returns_list_of_assets():
    response = await ddb.get_assets()
    assert isinstance(response, list)
    assert isinstance(response[0], Asset)
