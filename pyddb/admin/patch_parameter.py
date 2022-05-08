from pyddb import DDBClient
from pyddb.models import ParameterType


async def patch_parameter_type(
    parameter_type: ParameterType,
    default_unit_id: str = None,
    name: str = None,
    data_type: str = None,
):
    body = {}
    if default_unit_id:
        body["default_unit_id"] = default_unit_id
    if name:
        body["name"] = name
    if data_type:
        body["data_type"] = data_type

    response = await DDBClient.delete_request(
        endpoint=f"parameter_types/{parameter_type.id}", body=body
    )
    return response
