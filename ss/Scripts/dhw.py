from ddb_client import *
import asyncio
import time


async def process(project_number: str, flat_group_name: str):
    ddb = DDB(environment="sandbox")

    t = time.time()
    (
        number_of_baths,
        number_of_shower_trays,
        shower_in_bathroom,
        hot_water_consumption,
        storage_temp,
        cold_feed_temp,
        litres_per_second,
        m3,
        industry_guidance,
        derived_value,
        asset_types,
    ) = await asyncio.gather(
        ddb.get_parameter_types(search="Number of baths"),
        ddb.get_parameter_types(search="Number of shower trays"),
        ddb.get_parameter_types(search="Shower in bathroom"),
        ddb.get_parameter_types(search="Hot water consumption"),
        ddb.get_parameter_types(search="Storage temperature"),
        ddb.get_parameter_types(search="Cold feed temperature"),
        ddb.get_unit_by_name("l/s"),
        ddb.get_unit_by_name("m³"),
        ddb.get_source_type_by_name(name="Industry Guidance"),
        ddb.get_source_type_by_name(name="Derived Value"),
        ddb.get_asset_types(),
    )
    t1 = time.time()
    print(f"{t1-t0}s to gather data.")

    async def subprocess_1(assets: List[Asset]):
        def calc_hot_water_demand(
            no_baths: int, no_shower_trays: int, shower_in_bathroom: bool
        ):
            if no_baths == 0 and no_shower_trays == 1:
                return 0.15
            if no_baths == 0 and no_shower_trays >= 2:
                return 0.2
            if no_baths != 0 and no_shower_trays == 0:
                return 0.2
            if no_baths != 0 and no_shower_trays == 1 and shower_in_bathroom:
                return 0.2
            if no_baths != 0 and no_shower_trays == 1 and not shower_in_bathroom:
                return 0.25
            if no_baths != 0 and no_shower_trays == 2 and shower_in_bathroom:
                return 0.2
            if no_baths != 0 and no_shower_trays >= 2 and not shower_in_bathroom:
                return 0.35
            if no_baths != 0 and no_shower_trays >= 3 and shower_in_bathroom:
                return 0.3

        input_parameters = await ddb.get_parameters(
            asset_id=[a.id for a in assets],
            parameter_type_id=[
                pt[0].id
                for pt in [number_of_baths, number_of_shower_trays, shower_in_bathroom]
            ],
            page_limit=9999,
        )

        input_asset_parameters = [
            [p for p in input_parameters if p.parents[0].id == asset.id]
            for asset in assets
        ]
        sources = await project.post_sources(
            sources=[
                NewSource(
                    source_type=industry_guidance,
                    title="NHBC",
                    reference="Table 4",
                )
            ]
        )
        source = sources[0]
        new_parameters = []
        new_assets = []

        for asset_parameters in input_asset_parameters:
            # if all inputs exist and have values
            if len(asset_parameters) == 3 and all(
                [parameter.revision for parameter in asset_parameters]
            ):
                new_parameters.append(
                    NewParameter(
                        parameter_type=hot_water_consumption,
                        revision=NewRevision(
                            value=calc_hot_water_demand(
                                no_baths=next(
                                    (
                                        p.revision.values[0].value
                                        for p in asset_parameters
                                        if p.parameter_type.name == "Number of baths"
                                    ),
                                    None,
                                ),
                                no_shower_trays=next(
                                    (
                                        p.revision.values[0].value
                                        for p in asset_parameters
                                        if p.parameter_type.name
                                        == "Number of shower trays"
                                    ),
                                    None,
                                ),
                                shower_in_bathroom=next(
                                    (
                                        p.revision.values[0].value
                                        for p in asset_parameters
                                        if p.parameter_type.name == "Shower in bathroom"
                                    ),
                                    None,
                                ),
                            ),
                            unit=litres_per_second,
                            source=source,
                        ),
                    )
                )
                new_assets.append(next((p.parents[0] for p in asset_parameters), None))

        await ddb.post_parameters(parameters=new_parameters, assets=new_assets)

    async def subprocess_2():
        def calc_hot_water_load(
            hot_water_demand: float, storage_temp: float, cold_feed_temp: float
        ):
            return hot_water_demand * 4.2 * (storage_temp - cold_feed_temp)

    projects = await ddb.get_projects(number=project_number)
    project = projects[0]
    building_type = await ddb.get_asset_type_by_name("building")
    buildings = await project.get_assets(asset_type_id=building_type.id)

    # await asyncio.gather(
    #     *[process_building(building=building) for building in buildings]
    # )


if __name__ == "__main__":

    t0 = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process(project_number="11252300", flat_group_name="Flats"))
    t1 = time.time()
    print(f"{t1-t0}s")
