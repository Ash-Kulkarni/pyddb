from pyddb.admin import NewAssetType
from pyddb import DDBClient
from pyddb.admin.new_types import NewAssetSubtype


async def post_asset_sub_type(new_asset_sub_type: NewAssetSubtype):
    body = {
        "asset_sub_types": [
            {
                "id": new_asset_sub_type.id,
                "name": new_asset_sub_type.name,
                "asset_type_id": new_asset_sub_type.asset_type,
            }
        ]
    }

    if new_asset_sub_type.parent_asset_sub_type:
        body["asset_sub_types"][0][
            "parent_asset_sub_type_id"
        ] = new_asset_sub_type.parent_asset_sub_type

    response = await DDBClient.post_request(
        endpoint=f"asset_types{new_asset_sub_type.asset_type.id}/asset_sub_types",
        body=body,
    )
    return response
