from pyddb import DDB, Parameter
import pytest

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_parameters():
    response = await ddb.get_parameters()
    assert isinstance(response, list)
    assert isinstance(response[0], Parameter)
