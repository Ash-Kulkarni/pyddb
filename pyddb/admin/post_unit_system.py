from pyddb import DDBClient
from pyddb.admin.new_types import NewUnitSystem


async def post_unit_type(new_unit_system: NewUnitSystem):
    print("No current endpoint for posting new unit systems.")
    pass
    # body = {"unit_systems": [{"id": new_unit_system.id, "name": new_unit_system.name}]}

    # response = await DDBClient.post_request(endpoint="unit_systems", body=body)
    # return response
