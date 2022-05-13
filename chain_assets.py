from typing import List
import asyncio
from pyddb import Project, Asset, NewAsset, DDB

async def main():
    ddb = DDB()
    ddb.set_environment("sandbox")


async def post_asset_chain():
    self = "self"
    ddb = DDB()

    new_assets = List[NewAsset]

    # get all assets that are being posted to an existing asset
    # sort in order of hierarchy
    # for each asset, check if the parent has any children with the same name and type
    # if so update the newasset to the asset, add any  newassets that have this aseset as their parent to the list
    # post all newassets in hierarchy order

    a = [asset for asset in new_assets if isinstance(asset.parent, Asset)]
    for x in a:
        existing_asset = next(
            (
                y
                for y in await x.parent.get_assets()
                if (y.name, y.asset_type) == (x.name, x.asset_type)
            ),
            None,
        )
        if existing_asset:
            x = existing_asset
            for asset in new_assets:
                if asset.parent == x:
                    a.append(asset)

    ddb.get_assets()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
