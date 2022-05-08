from pyddb import DDBClient
from pyddb.admin.new_types import NewUnitType


async def post_unit_type(new_unit_type: NewUnitType):
    body = {"unit_types": [{"id": new_unit_type.id, "name": new_unit_type.name}]}

    response = await DDBClient.post_request(endpoint="unit_types", body=body)
    return response
