from pyddb import DDB, Parameter, BaseURL
import pytest

ddb = DDB(url=BaseURL.sandbox)


@pytest.mark.asyncio
async def test_returns_list_of_parameters():
    response = await ddb.get_parameters(page_limit=5)
    assert isinstance(response, list)
    assert isinstance(response[0], Parameter)
