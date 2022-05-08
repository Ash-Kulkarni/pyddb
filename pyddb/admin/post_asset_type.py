from pyddb.admin import NewAssetType
from pyddb import DDBClient


async def post_asset_type(new_asset_type: NewAssetType):
    body = {
        "asset_types": [
            {
                "id": new_asset_type.id,
                "name": new_asset_type.name,
                "parent": new_asset_type.parent,
                "asset_sub_type": new_asset_type.asset_sub_type,
            }
        ]
    }

    if new_asset_type.asset_type_group_id:
        body["asset_types"][0][
            "asset_type_group_id"
        ] = new_asset_type.asset_type_group_id

    response = await DDBClient.post_request(endpoint="asset_types", body=body)
    return response
