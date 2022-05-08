from ddb_client import *
import asyncio


@time_function
async def process(project_number: str, flat_group_name: str):
    ddb = DDB(environment="sandbox")

    (
        number_of_bedrooms,
        daily_water_consumption,
        cold_water_diversity,
        diversified_volume_parameter,
        litres,
        m3,
        industry_guidance,
        derived_value,
        asset_types,
    ) = await asyncio.gather(
        ddb.get_parameter_types(search="Number of bedrooms"),
        ddb.get_parameter_types(search="Daily cold water consumption"),
        ddb.get_parameter_types(search="Domestic cold water diversity factor"),
        ddb.get_parameter_types(search="Diversified volume"),
        ddb.get_unit_by_name("litres"),
        ddb.get_unit_by_name("m³"),
        ddb.get_source_type_by_name(name="Industry Guidance"),
        ddb.get_source_type_by_name(name="Derived Value"),
        ddb.get_asset_types(),
    )

    system = next((a for a in asset_types if a.name == "system"), None)
    subsystem = next((a for a in asset_types if a.name == "sub system"), None)
    product_type = next((a for a in asset_types if a.name == "product type"), None)

    @time_function
    async def subprocess_1(project: Project, assets: List[Asset]):
        def dwelling_consumption(bedrooms: int):
            # number of bedrooms: daily demand (l) per bedroom - 3 indicates 3 or more bedrooms
            cw_consumption = {1: 210, 2: 130, 3: 100}
            if bedrooms > 3:
                return bedrooms * cw_consumption[3]
            else:
                return bedrooms * cw_consumption[bedrooms]

        input_parameters = await ddb.get_parameters(
            asset_id=[a.id for a in assets],
            parameter_type_id=number_of_bedrooms[0].id,
            page_limit=9999,
        )

        # inputs = {p.parents[0].id: p.revision.values[0].value for p in input_parameters}
        [source] = await project.post_sources(
            sources=[
                NewSource(
                    source_type=industry_guidance,
                    title="Institute of Plumbing - Plumbing Engineering Services Design Guide",
                    reference="Table 2",
                )
            ]
        )
        new_parameters = []
        new_assets = []
        for parameter in input_parameters:
            if parameter.revision:
                new_parameters.append(
                    NewParameter(
                        parameter_type=daily_water_consumption[0],
                        revision=NewRevision(
                            value=dwelling_consumption(
                                parameter.revision.values[0].value
                            ),
                            unit=litres,
                            source=source,
                        ),
                    )
                )
                new_assets.append(parameter.parents[0])

        await ddb.post_parameters(parameters=new_parameters, assets=new_assets)

    @time_function
    async def subprocess_2(project: Project, building: Asset, assets: List[Asset]):

        parameters = await ddb.get_parameters(
            asset_id=[a.id for a in assets],
            parameter_type_id=daily_water_consumption[0].id,
            page_limit=9999,
        )
        total = sum(p.revision.values[0].value for p in parameters)

        sources = await project.post_sources(
            sources=[
                NewSource(
                    source_type=derived_value,
                    title="CWS Calc Process",
                    reference="Subprocess 2",
                )
            ]
        )
        source = sources[0]

        await building.post_parameters(
            parameters=[
                NewParameter(
                    parameter_type=daily_water_consumption[0],
                    revision=NewRevision(value=total, unit=litres, source=source),
                )
            ]
        )

    @time_function
    async def subprocess_3(project: Project, building: Asset):

        parameters = await building.get_parameters(
            parameter_type_id=[
                daily_water_consumption[0].id,
                cold_water_diversity[0].id,
            ],
            page_limit=9999,
        )

        volume = next(
            (
                p
                for p in parameters
                if p.parameter_type.name == "Daily cold water consumption"
            ),
            None,
        )
        diversity = next(
            (
                p
                for p in parameters
                if p.parameter_type.name == "Domestic cold water diversity factor"
            ),
            None,
        )

        if volume and diversity:
            diversified_volume = (
                float(
                    volume.revision.values[0].value * diversity.revision.values[0].value
                )
                / 1000
            )
            [systems] = await building.post_assets(
                assets=[NewAsset(asset_type=system, name="Domestic Cold Water")]
            )

            [subsystems] = await systems.post_assets(
                assets=[NewAsset(asset_type=subsystem, name="Domestic Cold Water")]
            )

            [product_types] = await subsystems.post_assets(
                assets=[
                    NewAsset(asset_type=product_type, name="Cold Water Storage Tank")
                ]
            )
            sources = await project.post_sources(
                sources=[
                    NewSource(
                        source_type=derived_value,
                        title="CWS Calc Process",
                        reference="Subprocess 2",
                    )
                ]
            )
            source = sources[0]
            await product_types.post_parameters(
                parameters=[
                    NewParameter(
                        parameter_type=diversified_volume_parameter[0],
                        revision=NewRevision(
                            value=diversified_volume, unit=m3, source=source
                        ),
                    )
                ]
            )

    async def process_building(building: Asset):
        space_type = await ddb.get_asset_type_by_name("space type")
        space_types = await building.get_assets(asset_type_id=space_type.id)
        flats = next((s for s in space_types if s.name == flat_group_name), None)
        if flats:
            building_flats = await flats.get_assets()

            await subprocess_1(project=project, assets=building_flats)

            await subprocess_2(
                project=project, building=building, assets=building_flats
            )

            await subprocess_3(project=project, building=building)

    [project] = await ddb.get_projects(number=project_number)

    building_type = await ddb.get_asset_type_by_name("building")
    buildings = await project.get_assets(asset_type_id=building_type.id)

    await asyncio.gather(
        *[process_building(building=building) for building in buildings]
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process(project_number="11252300", flat_group_name="Flats"))
