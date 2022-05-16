from typing import List
import asyncio
from pyddb import Project, Asset, NewAsset, DDB, AssetType


async def main():
    ddb = DDB()
    project = await ddb.post_project(project_number="21515700")
    asset_types = await ddb.get_asset_types()

    new_assets = [
        my_site := NewAsset(
            asset_type=next(a for a in asset_types if a.name == "site"),
            name="Chain 23w43e2",
            parent=None,
        ),
        my_building := NewAsset(
            asset_type=next(a for a in asset_types if a.name == "building"),
            name="Chain 2",
            parent=my_site,
        ),
        my_system := NewAsset(
            asset_type=next(a for a in asset_types if a.name == "system"),
            name="Chain 3",
            parent=my_building,
        ),
        my_sub_system := NewAsset(
            asset_type=next(a for a in asset_types if a.name == "sub system"),
            name="Chain 3",
            parent=my_system,
        ),
    ]

    await project.post_assets(assets=new_assets)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
