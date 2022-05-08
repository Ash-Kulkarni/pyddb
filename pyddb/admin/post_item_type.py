from pyddb import DDBClient
from pyddb.admin.new_types import NewItemType


async def post_item_type(new_item_type: NewItemType):
    body = {
        "item_types": [
            {
                "id": new_item_type.id,
                "parameter_type_id": new_item_type.parameter_type.id,
            }
        ]
    }

    if new_item_type.asset_type:
        body["item_types"][0]["asset_type_id"] = new_item_type.asset_type.id

    response = await DDBClient.post_request(endpoint="item_types", body=body)
    return response
