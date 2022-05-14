from pyddb import DDB, Asset, NewAsset, get_asset_type_by_name
import pytest


async def get_test_asset():
    ddb = DDB()
    [asset] = await ddb.get_assets(asset_id="34ad3f99-e1c4-42f0-8a71-dcaa75315efd")
    return asset


@pytest.mark.asyncio
async def test_same_new_asset_is_equal():
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Dalkeith Road", parent=None
    )
    assert new_asset == new_asset


@pytest.mark.asyncio
async def test_different_new_asset_is_not_equal():
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Dalkeith Road", parent=None
    )
    other_new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Not Dalkeith Road", parent=None
    )
    assert new_asset != other_new_asset


@pytest.mark.asyncio
async def test_new_asset_is_equal_to_same_asset():
    asset = await get_test_asset()
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Dalkeith Road", parent=None
    )
    assert new_asset == asset


@pytest.mark.asyncio
async def test_new_asset_is_not_equal_to_different_asset():
    asset = await get_test_asset()
    new_asset = NewAsset(
        asset_type=get_asset_type_by_name("site"), name="Haymarket", parent=None
    )
    assert new_asset != asset
