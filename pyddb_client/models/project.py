from typing import Optional, List
import aiohttp
import asyncio
import pyddb_client.models as models


class Project(models.DDBClient):
    centre_code: str
    job_number: str
    job_name_short: str
    organisation_name: Optional[str]
    project_director_name: str
    project_manager_name: str
    project_url: str
    scope_of_works: Optional[str]
    project_manager_email: str
    project_director_email: str
    job_suffix: str
    project_code: str
    confidential: bool
    project_id: str
    number: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    def __repr__(self) -> str:
        return repr(f"Name: {self.job_name_short}, Project Number: {self.project_code}")

    async def get_assets(self, **kwargs):
        return await super().get_assets(project_id=self.project_id, **kwargs)

    async def get_parameters(self, **kwargs):
        return await super().get_parameters(project_id=self.project_id, **kwargs)

    async def post_sources(self, sources: List["models.NewSource"]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)

    async def post_parameters(
        self,
        parameters: List["models.NewParameter"],
    ):
        existing_parameters = await self.get_parameters(
            parameter_type_id=[p.parameter_type.id for p in parameters]
        )
        existing_parameter_type_ids = [p.parameter_type.id for p in existing_parameters]

        new_parameters = [
            p
            for p in parameters
            if p.parameter_type.id not in existing_parameter_type_ids
        ]
        existing_parameter_revisions = [
            (
                p.parameter_type.id,
                p.revision.values[0].value,
                p.revision.values[0].unit.id if p.revision.values[0].unit else None,
                p.revision.source.id,
            )
            for p in existing_parameters
            if p.revision
        ]

        for parameter in existing_parameters:
            if parameter.parameter_type.id in [p.parameter_type.id for p in parameters]:
                p = next(
                    (
                        p
                        for p in parameters
                        if p.parameter_type.id == parameter.parameter_type.id
                    ),
                    None,
                )
                setattr(p, "id", parameter.id)

        new_revisions = [
            p
            for p in parameters
            if p.revision
            and p not in new_parameters
            and (
                p.parameter_type.id,
                p.revision.value,
                p.revision.unit.id if p.revision.unit else None,
                p.revision.source.id,
            )
            not in existing_parameter_revisions
        ]

        tasks = []
        if new_parameters:
            tasks.append(self.post_new_parameters(parameters=new_parameters))
        if new_revisions:
            tasks.append(self.post_new_revisions(parameters=new_revisions))
        if tasks:
            return await asyncio.gather(*tasks)
        return None

    async def post_new_parameters(self, parameters: List["models.NewParameter"]):
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
