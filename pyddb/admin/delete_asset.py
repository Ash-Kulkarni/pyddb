from pyddb import DDBClient, Asset


async def delete_asset(asset: Asset):

    response = await DDBClient.delete_request(endpoint=f"assets/{asset.id}")
    return response
