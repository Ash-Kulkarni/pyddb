from pyddb import DDB, Parameter, ParameterType, BaseURL
import pytest

ddb = DDB(url=BaseURL.sandbox)


@pytest.mark.asyncio
async def test_returns_list_of_parameter_types():
    response = await ddb.get_parameter_types()
    assert isinstance(response, list)
    assert isinstance(response[0], ParameterType)
