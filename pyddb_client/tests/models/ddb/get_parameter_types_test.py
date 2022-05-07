from pyddb_client.models import DDB, Parameter
import pytest

from pyddb_client.models.parameter_type import ParameterType

ddb = DDB()


@pytest.mark.asyncio
async def test_returns_list_of_parameter_types():
    response = await ddb.get_parameter_types()
    assert isinstance(response, list)
    assert isinstance(response[0], ParameterType)
