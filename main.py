from typing import List
import asyncio
from pyddb import Project, Asset, NewSource, NewParameter, NewRevision, NewAsset, DDB
from pyddb.utils import (
    get_parameter_type_by_name,
    get_parameter_types_by_name,
    get_asset_type_by_name,
    get_source_type_by_name,
    get_unit_by_name,
    regenerate_all_types,
    time_function,
)


async def process(project_number: str, flat_group_name: str):
    ddb = DDB()
    ddb.set_environment("sandbox")

    await regenerate_all_types()

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
            parameter_type_id=get_parameter_type_by_name("Number of bedrooms").id,
            page_limit=9999,
        )

        # inputs = {p.parents[0].id: p.revision.values[0].value for p in input_parameters}
        [source] = await project.post_sources(
            sources=[
                NewSource(
                    source_type=get_source_type_by_name("Industry Guidance"),
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
                        parameter_type=get_parameter_type_by_name(
                            "Daily cold water consumption"
                        ),
                        revision=NewRevision(
                            value=dwelling_consumption(
                                parameter.revision.values[0].value
                            ),
                            unit=get_unit_by_name("litres"),
                            source=source,
                        ),
                    )
                )
                new_assets.append(parameter.parents[0])

        await ddb.post_parameters(parameters=new_parameters, assets=new_assets)

    async def subprocess_2(project: Project, building: Asset, assets: List[Asset]):

        parameters = await ddb.get_parameters(
            asset_id=[a.id for a in assets],
            parameter_type_id=get_parameter_type_by_name(
                "Daily cold water consumption"
            ).id,
        )
        total = sum(p.revision.values[0].value for p in parameters)

        [source] = await project.post_sources(
            sources=[
                NewSource(
                    source_type=get_source_type_by_name("Derived Value"),
                    title="CWS Calc Process",
                    reference="Subprocess 2",
                )
            ]
        )

        await building.post_parameters(
            parameters=[
                NewParameter(
                    parameter_type=get_parameter_type_by_name(
                        "Daily cold water consumption"
                    ),
                    revision=NewRevision(
                        value=total, unit=get_unit_by_name("litres"), source=source
                    ),
                )
            ]
        )

    async def subprocess_3(project: Project, building: Asset):

        parameters = await building.get_parameters(
            parameter_type_id=[
                p.id
                for p in get_parameter_types_by_name(
                    [
                        "Daily cold water consumption",
                        "Domestic cold water diversity factor",
                    ]
                )
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

            systems = await building.post_assets(
                assets=[
                    NewAsset(
                        asset_type=get_asset_type_by_name("system"),
                        name="Domestic Cold Water",
                    )
                ]
            )

            subsystems = await systems[0].post_assets(
                assets=[
                    NewAsset(
                        asset_type=get_asset_type_by_name("sub system"),
                        name="Domestic Cold Water",
                    )
                ]
            )

            product_types = await subsystems[0].post_assets(
                assets=[
                    NewAsset(
                        asset_type=get_asset_type_by_name("product type"),
                        name="Cold Water Storage Tank",
                    )
                ]
            )
            sources = await project.post_sources(
                sources=[
                    NewSource(
                        source_type=get_source_type_by_name("Derived Value"),
                        title="CWS Calc Process",
                        reference="Subprocess 3",
                    )
                ]
            )
            source = sources[0]
            await product_types[0].post_parameters(
                parameters=[
                    NewParameter(
                        parameter_type=get_parameter_type_by_name("Diversified volume"),
                        revision=NewRevision(
                            value=diversified_volume,
                            unit=get_unit_by_name("m³"),
                            source=source,
                        ),
                    )
                ]
            )

    async def process_building(building: Asset):
        space_types = await building.get_assets(
            asset_type_id=get_asset_type_by_name("space type").id
        )
        flats = next((s for s in space_types if s.name == flat_group_name), None)

        if flats:
            building_flats = await flats.get_assets()

            await subprocess_1(project=project, assets=building_flats)

            await subprocess_2(
                project=project, building=building, assets=building_flats
            )

            await subprocess_3(project=project, building=building)

    [project] = await ddb.get_projects(number=project_number)

    buildings = await project.get_assets(
        asset_type_id=get_asset_type_by_name("building").id
    )

    await asyncio.gather(
        *[process_building(building=building) for building in buildings]
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process(project_number="11252300", flat_group_name="Flats"))
