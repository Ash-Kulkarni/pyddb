from pyddb import DDB, Asset, NewAsset
from pyddb.utils import get_asset_type_by_name
import pytest


async def get_test_asset():
    ddb = DDB()
    [asset] = await ddb.get_assets(asset_id="34ad3f99-e1c4-42f0-8a71-dcaa75315efd")
    return asset


@pytest.mark.asyncio
async def test_same_asset_is_equal():
    asset = await get_test_asset()
    assert asset == asset


@pytest.mark.asyncio
async def test_different_asset_is_not_equal():
    asset = await get_test_asset()
    ddb = DDB()
    [other_asset] = await ddb.get_assets(
        asset_id="66a075a4-1b2e-4347-ab46-ed95e63ea57a"
    )
    assert asset != other_asset


@pytest.mark.asyncio
async def test_asset_is_equal_to_same_new_asset():
    asset = await get_test_asset()
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Dalkeith Road", parent=None
    )
    assert asset == new_asset


@pytest.mark.asyncio
async def test_asset_is_not_equal_to_different_new_asset():
    asset = await get_test_asset()
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Haymarket", parent=None
    )
    assert asset != new_asset
