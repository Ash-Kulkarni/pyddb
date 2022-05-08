from pyddb.admin import NewAssetType
from pyddb import DDBClient
from pyddb.admin.new_types import NewParameterType


async def post_parameter_type(new_parameter_type: NewParameterType):
    body = {
        "parameter_types": [
            {
                "id": new_parameter_type.id,
                "name": new_parameter_type.name,
                "data_type": new_parameter_type.data_type,
                "global_parameter": new_parameter_type.global_parameter,  # global_parameter,
            }
        ]
    }

    if new_parameter_type.default_unit:
        body["parameter_types"][0][
            "default_unit_id"
        ] = new_parameter_type.default_unit.id

    response = await DDBClient.post_request(endpoint="parameter_types", body=body)
    return response
