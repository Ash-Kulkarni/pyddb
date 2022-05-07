from typing import Optional, Union, List
import aiohttp
import asyncio

import pyddb_client.models as models


class Asset(models.DDBClient):
    id: str
    name: str
    project_id: str
    parent: Optional[str]
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    asset_sub_type: Optional[Union[Optional[bool], models.AssetSubType]] = None
    asset_type_group: Optional[models.AssetTypeGroup] = None
    children: List[str]
    asset_type: Optional[models.AssetType]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}, ID: {self.id}")

    async def get_assets(self, **kwargs):
        return await super().get_assets(parent_id=[self.id], **kwargs)

    async def get_parameters(self, **kwargs):
        return await super().get_parameters(**kwargs)

    async def post_sources(self, sources: List[models.NewSource]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)

    async def post_assets(
        self,
        assets: List[models.NewAsset],
    ):
        body = {"assets": []}

        for asset in assets:
            body["assets"].append(
                {
                    "asset_type_id": asset.asset_type.id,
                    "project_id": self.project_id,
                    "name": asset.name,
                    "parent_id": self.id,
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
                return [Asset(**x) for x in response_list]
            if response.status == 400:
                existing_assets = await self.get_assets(
                    asset_type_id=[a.asset_type.id for a in assets],
                )
                return [
                    asset
                    for asset in existing_assets
                    if asset.name in [a.name for a in assets]
                ]

    async def post_parameters(self, parameters: List[models.NewParameter]):
        assets = [self] * len(parameters)
        return await super().post_parameters(parameters, assets)

    async def post_new_parameters(self, parameters: List[models.NewParameter]):
        body = {"parameters": []}
        for parameter in parameters:
            if not parameter.revision:
                body["parameters"].append(
                    {
                        "parameter_type_id": parameter.parameter_type.id,
                        "project_id": self.project_id,
                    }
                )
            else:
                # if parent_ids[i]:
                #     body["parameters"][i]["parent_ids"] = [parent_ids[i]]
                body["parameters"].append(
                    {
                        "parameter_type_id": parameter.parameter_type.id,
                        "project_id": self.project_id,
                        "parent_ids": [self.id],
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
            response_key="parameters",
            cls=models.Parameter,
        )
        if response.status == 400:
            res = await response.json()
            print(res["details"])
        return response

    async def post_new_revision(self, parameter: models.NewParameter):

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

    async def post_new_revisions(self, parameters: List[models.NewParameter]):
        return await asyncio.gather(
            *[self.post_new_revision(parameter=parameter) for parameter in parameters]
        )
