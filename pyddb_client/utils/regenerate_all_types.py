from pyddb_client.models import DDB
from utils.write_data import write_data
import asyncio


async def regenerate_all_types():
    ddb = DDB()

    (
        source_types,
        parameter_types,
        asset_types,
        unit_types,
        unit_systems,
        units,
        tags,
        tag_types,
    ) = await asyncio.gather(
        ddb.get_source_types(),
        ddb.get_parameter_types(),
        ddb.get_asset_types(),
        ddb.get_unit_types(),
        ddb.get_unit_systems(),
        ddb.get_units(),
        ddb.get_tags(),
        ddb.get_tag_types(),
    )

    # await write_data("source_types", data={1: 2})

    await asyncio.gather(
        write_data("source_types", source_types),
        write_data("parameter_types", parameter_types),
        write_data("asset_types", asset_types),
        write_data("unit_types", unit_types),
        write_data("unit_systems", unit_systems),
        write_data("units", units),
        write_data("tags", tags),
        write_data("tag_types", tag_types),
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(regenerate_all_types())
