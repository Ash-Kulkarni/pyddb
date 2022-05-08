from pyddb_client import DDB, Parameter, ParameterType
import pytest

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_parameter_types():
    response = await ddb.get_parameter_types()
    assert isinstance(response, list)
    assert isinstance(response[0], ParameterType)
