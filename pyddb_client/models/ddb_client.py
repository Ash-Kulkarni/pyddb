from typing import Optional, Union, List, Type
from pydantic import BaseModel
from DDBpy_auth import DDBAuth  # https://github.com/arup-group/ddbpy_auth
import asyncio
import aiohttp
import pyddb_client.models as models
import pyddb_client.utils as utils


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DDBClient(BaseModel):
    environment = "sandbox"
    base_urls = {
        "prod": "https://ddb.arup.com/api/",
        "dev": "https://dev.ddb.arup.com/api/",
        "sandbox": "https://sandbox.ddb.arup.com/api/",
    }
    url: str = base_urls[environment]
    headers = {
        "Authorization": "Bearer " + DDBAuth().acquire_new_access_content(),
        "version": "0",
    }

    def set_environment(self, environment: str):
        """Change which environment this client is pointed to.

        Args:
            environment (str): Must be "sandbox", "prod", or "dev"
        """
        self.environment = environment
        self.url = self.base_urls[environment]

    async def get_request(self, endpoint: str, response_key: str, cls: Type, **kwargs):
        payload = utils.generate_payload(**kwargs)
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.url}{endpoint}",
                params=payload,
                headers=self.headers,
                ssl=False,
            )
            result = await response.json()
        return [cls.parse_obj(x) for x in result[response_key]]

    async def post_request(self, endpoint: str, body: dict):
        async with aiohttp.ClientSession() as session:
            return await session.post(
                f"{self.url}{endpoint}",
                json=body,
                headers=self.headers,
                ssl=False,
            )

    async def get_sources(self, **kwargs):

        """Retreives list of source objects.

        Retrieves a list containing all sources in the DDB database.
        Sources can be filtered by various keywords.

        Args:
            **source_id (str): Source instance GUIDs to return.
            **reference_id (str): Project GUIDs to retreive sources for.
            **source_type_id (str): Source type GUIDs to filter by.
            **title (str): Source titles to return, must be an exact match.
            **reference (str): Source references to return, must be an exact match.

        Returns:
            A list of dictionaries of ddb sources.
        """
        return await self.get_request(
            endpoint="sources", response_key="sources", cls=models.Source, **kwargs
        )

    async def get_parameters(self, **kwargs):
        """Retreives list of all parameter objects.

        Returns a list of all parameter instances, can be filtered by various keyword arguments:

        Args:
            **asset_id (str): Asset instance GUID
            **asset_type (str): Asset type GUID
            **parameter_id (str): Parameter instance GUID
            **parameter_type_id (str): Parameter type GUID
            **project_id (str): Project instance GUID
            **category_id (str): Tag instance GUID
            **report_id (str): Tag instance GUID
            **discipline_id (str): Tag instance GUID
            **source_id (str): Source instance GUID
            **source_type_id (str): Source type GUID
            **qa_status (str): Must be one of: "unanswered", "answered", "checked", "approved", or "rejected"
            **unit_id (str): Unit GUID

        Returns:
            List of parameter type dictionaries.
        """
        return await self.get_request(
            endpoint="parameters",
            response_key="parameters",
            cls=models.Parameter,
            **kwargs,
        )

    async def get_assets(self, **kwargs):
        """Gets list of all asset instance objects.

        Gets all assets from DDB, can be filtered by various keywords:

        Args:
            asset_id (str): Asset instance GUID.
            asset_type_id (str): Asset type GUID.
            parent_id (str): Parent asset instance GUID.
            project_id (str): Project instance GUID.

        Returns:
            List of asset dictionaries.
        """
        return await self.get_request(
            endpoint="assets", response_key="assets", cls=models.Asset, **kwargs
        )

    async def post_source(self, source: "models.NewSource", reference_id):
        existing_source = await self.get_sources(
            reference_id=reference_id,
            source_type_id=source.source_type.id,
            title=source.title,
            reference=source.reference,
        )
        if existing_source != []:
            return existing_source[0]
        else:
            body = {
                "source_type_id": source.source_type.id,
                "title": source.title,
                "reference": source.reference,
                "reference_id": reference_id,
                "reference_table": "projects",
                "reference_url": "https://ddb.arup.com/project",
            }
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f"{self.url}sources",
                    json=body,
                    headers=self.headers,
                    ssl=False,
                )
                result = await response.json()
                response = result["source"]
            return models.Source(**response)

    async def post_sources(self, sources: List["models.NewSource"], reference_id: str):

        return await asyncio.gather(
            *[
                self.post_source(source=source, reference_id=reference_id)
                for source in sources
            ]
        )

    async def post_assets(
        self,
        assets: List["models.NewAsset"],
    ):
        body = {"assets": []}

        for asset in assets:
            body["assets"].append(
                {
                    "asset_type_id": asset.asset_type.id,
                    "project_id": self.project_id,
                    "name": asset.name,
                }
            )

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.url}assets",
                json=body,
                headers=self.headers,
                ssl=False,
            )

            if response.status == 201:
                result = await response.json()
                response_list = result["assets"]
                return [models.Asset(**x) for x in response_list]
            if response.status == 400:
                existing_assets = await self.get_assets(
                    asset_type_id=[a.asset_type.id for a in assets],
                )
                return [
                    asset
                    for asset in existing_assets
                    if asset.name in [a.name for a in assets]
                ]

    async def post_parameters(
        self, parameters: List["models.NewParameter"], assets: List["models.Asset"]
    ):
        existing_parameters = await DDBClient.get_parameters(
            self,
            parameter_type_id=[p.parameter_type.id for p in parameters],
            asset_id=[a.id for a in assets],
        )
        existing_parameter_type_asset_list = [
            (p.parameter_type.id, p.parents[0].id) for p in existing_parameters
        ]
        existing_revisions = [
            [
                p.parameter_type.id,
                p.parents[0].id,
                str(p.revision.values[0].value),
                p.revision.values[0].unit.id,
                p.revision.source.id,
            ]
            for p in existing_parameters
        ]

        new_revisions = []
        new_parameters = []
        new_parameter_assets = []
        for parameter, asset in list(zip(parameters, assets)):
            if [
                parameter.parameter_type.id,
                asset.id,
                parameter.revision.value,
                parameter.revision.unit.id,
                parameter.revision.source.id,
            ] in existing_revisions:
                continue
            elif (
                parameter.parameter_type.id,
                asset.id,
            ) in existing_parameter_type_asset_list:
                setattr(
                    parameter,
                    "id",
                    next(
                        (
                            p.id
                            for p in existing_parameters
                            if (parameter.parameter_type.id, asset.id)
                            == (p.parameter_type.id, p.parents[0].id)
                        )
                    ),
                )
                new_revisions.append(parameter)
            else:
                new_parameters.append(parameter)
                new_parameter_assets.append(asset)

        tasks = []
        if new_parameters:
            tasks.append(
                self.post_new_parameters(
                    parameters=new_parameters, assets=new_parameter_assets
                )
            )
        if new_revisions:
            tasks.append(self.post_new_revisions(parameters=new_revisions))
        if tasks:
            return await asyncio.gather(*tasks)
        return None

    async def post_new_parameters(
        self, parameters: List["models.NewParameter"], assets: List["models.Asset"]
    ):
        body = {"parameters": []}
        for parameter, asset in list(zip(parameters, assets)):
            if not parameter.revision:
                body["parameters"].append(
                    {
                        "parameter_type_id": parameter.parameter_type.id,
                        "project_id": asset.project_id,
                    }
                )
            else:

                body["parameters"].append(
                    {
                        "parameter_type_id": parameter.parameter_type.id,
                        "project_id": asset.project_id,
                        "parent_ids": [asset.id],
                        "revision": {
                            "source_id": parameter.revision.source.id,
                            "comment": parameter.revision.comment,
                            "location_in_source": parameter.revision.location_in_source,
                            "values": [
                                {
                                    "value": parameter.revision.value,
                                    "unit_id": parameter.revision.unit.id
                                    if parameter.revision.unit
                                    else None,
                                }
                            ],
                        },
                    }
                )
        response = await self.post_request(
            endpoint="parameters",
            body=body,
        )
        if response.status == 400:
            res = await response.json()
            print(res["details"])
        return response

    async def post_new_revision(self, parameter: "models.NewParameter"):

        updated_parameter = {
            "source_id": parameter.revision.source.id,
            "values": [
                {
                    "value": parameter.revision.value,
                    "unit_id": parameter.revision.unit.id
                    if parameter.revision.unit
                    else None,
                }
            ],
        }
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.url}parameters/{parameter.id}/revision",
                json=updated_parameter,
                headers=self.headers,
                ssl=False,
            )
            return await response.json()

    async def post_new_revisions(self, parameters: List["models.NewParameter"]):
        return await asyncio.gather(
            *[self.post_new_revision(parameter=parameter) for parameter in parameters]
        )
