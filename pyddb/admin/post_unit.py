from pyddb import DDBClient
from pyddb.admin.new_types import NewUnit


async def post_unit(new_unit: NewUnit):
    body = {
        "units": [
            {
                "id": new_unit.id,
                "name": new_unit.name,
                "unit_type_id": new_unit.unit_type.id,
                "unit_system_id": new_unit.unit_system.id,
            }
        ]
    }

    response = await DDBClient.post_request(endpoint="units", body=body)
    return response
