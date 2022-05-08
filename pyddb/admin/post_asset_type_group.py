from pyddb.admin import NewAssetType
from pyddb import DDBClient
from pyddb.admin.new_types import NewAssetTypeGroup


async def post_asset_type_group(new_asset_type_group: NewAssetTypeGroup):
    body = {
        "asset_type_groups": [
            {
                "id": new_asset_type_group.id,
                "name": new_asset_type_group.name,
            }
        ]
    }

    response = await DDBClient.post_request(endpoint="asset_type_groups", body=body)
    return response
