from typing import Optional, Union, List, Type
import aiohttp
from pydantic import BaseModel
import asyncio
from uuid import uuid4
from DDBpy_auth import DDBAuth

import pandas as pd


def generate_payload(**kwargs):
    """Generates a dictionary of provided keywords and values."""
    return {key: value for (key, value) in kwargs.items()}


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
        payload = generate_payload(**kwargs)
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

    async def delete_request(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            return await session.delete(
                f"{self.url}{endpoint}",
                headers=self.headers,
                ssl=False,
            )

    async def patch_request(self, endpoint: str, body: dict):
        async with aiohttp.ClientSession() as session:
            return await session.delete(
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
            endpoint="sources", response_key="sources", cls=Source, **kwargs
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
            cls=Parameter,
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
            endpoint="assets", response_key="assets", cls=Asset, **kwargs
        )

    async def post_source(self, source: "NewSource", reference_id):
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
            return Source(**response)

    async def post_sources(self, sources: List["NewSource"], reference_id: str):

        return await asyncio.gather(
            *[
                self.post_source(source=source, reference_id=reference_id)
                for source in sources
            ]
        )

    async def post_assets(
        self,
        assets: List["NewAsset"],
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

    async def post_parameters(self, parameters: List["NewParameter"]):
        existing_parameters = await DDBClient.get_parameters(
            self,
            parameter_type_id=[p.parameter_type.id for p in parameters],
            asset_id=[p.parent.id for p in parameters],
        )
        existing_parameter_type_asset_list = [
            (p.parameter_type.id, p.parents[0].id) for p in existing_parameters
        ]
        existing_revisions = [
            [
                p.parameter_type.id,
                p.parents[0].id,
                str(p.revision.values[0].value),
                p.revision.values[0].unit.id if p.revision.values[0].unit else None,
                p.revision.source.id,
            ]
            for p in existing_parameters
        ]

        new_revisions = []
        new_parameters = []
        new_parameter_assets = []
        for parameter in parameters:
            if [
                parameter.parameter_type.id,
                parameter.parent.id,
                parameter.revision.value,
                parameter.revision.unit.id if parameter.revision.unit else None,
                parameter.revision.source.id,
            ] in existing_revisions:
                continue
            elif (
                parameter.parameter_type.id,
                parameter.parent.id,
            ) in existing_parameter_type_asset_list:
                setattr(
                    parameter,
                    "id",
                    next(
                        (
                            p.id
                            for p in existing_parameters
                            if (parameter.parameter_type.id, parameter.parent.id)
                            == (p.parameter_type.id, p.parents[0].id)
                        )
                    ),
                )
                new_revisions.append(parameter)
            else:
                new_parameters.append(parameter)
                new_parameter_assets.append(parameter.parent)

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
        self, parameters: List["NewParameter"], assets: List["Asset"]
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

    async def post_new_revision(self, parameter: "NewParameter"):

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

    async def post_new_revisions(self, parameters: List["NewParameter"]):
        return await asyncio.gather(
            *[self.post_new_revision(parameter=parameter) for parameter in parameters]
        )

    async def sources_df_wip(self):
        return pd.DataFrame(
            [vars(source) for source in await self.get_sources()],
            columns=["title", "reference", "source_type_name", "id"],
        )

        b = {
            "title": "Source Title",
            "reference": "Source Reference",
            "source_type_name": "Source Type",
            "id": "Source ID",
        }
        df_simple = df.copy()
        df_simple.rename(columns=b, inplace=True)

        return df_simple

    async def parameters_df_wip(self):
        return pd.DataFrame(
            [vars(parameter) for parameter in await self.get_parameters()],
            columns=[
                "parameter_type_name",
                "revision_values_0_value",
                "revision_values_0_unit_name",
                "revision_source_source_type_name",
                "revision_source_title",
                "revision_source_reference",
            ],
        )

        b = {
            "parameter_type_name": "Parameter Type",
            "revision_values_0_value": "Value",
            "revision_values_0_unit_name": "Unit",
            "revision_source_source_type_name": "Source Type",
            "revision_source_title": "Source Title",
            "revision_source_reference": "Source Reference",
        }
        df_simple = df.copy()
        df_simple.rename(columns=b, inplace=True)

        return df_simple


class DDB(DDBClient):
    async def get_projects(self, **kwargs):
        """Returns a list of project objects.

        Returns:
            List of project dictionaries.
        """
        return await super().get_request(
            endpoint="projects", response_key="projects", cls=Project, **kwargs
        )

    async def post_project(self, project_number: str, confidential: bool = False):
        body = {"number": str(project_number), "confidential": confidential}
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.url}projects",
                json=body,
                headers=self.headers,
                ssl=False,
            )
            if response.status == 409:
                print("Getting existing project...")
                response = await self.get_projects(number=project_number)
                return response[0]
            result = await response.json()
        return Project(**result["project"])

    async def get_source_types(self, **kwargs):
        """Retreives list of source types objects."""
        return await super().get_request(
            endpoint="source_types",
            response_key="source_types",
            cls=SourceType,
            **kwargs,
        )

    async def get_parameter_types(self, **kwargs):
        """Retreives list of parameter type objects.

        Returns a list of all parameter types, can be filtered by various keyword arguments:

        Args:
            **asset_type_id (str): Asset type GUID, will only return parameter_types available on the given asset_type.
            **not_asset_id (str): Asset instance GUID, will only return parameter_types that are not attached to the given asset_id.
            **not_project_id (str): Project instance GUID, will only return parameter_types that are not attached to the given project_id.

        Returns:
            List of parameter type dictionaries.
        """
        return await super().get_request(
            endpoint="parameter_types",
            response_key="parameter_types",
            cls=ParameterType,
            **kwargs,
        )

    async def get_asset_types(self, **kwargs):
        """Returns list of all asset types objects.

        Response can be filtered by various keywords:

        Args:
            project_id (str): Project instance GUID.
            parent_asset_id (str): Parent asset instance GUID.
            asset_type_group_id (str): Asset type group GUID.

        Returns:
            A list of asset type dictionaries.
        """
        return await super().get_request(
            endpoint="asset_types", response_key="asset_types", cls=AssetType, **kwargs
        )

    async def get_asset_type_groups(self, **kwargs):
        """Returns all asset type groups.

        Args:
            asset_type_group_id (str): Asset type group GUID.

        Returns:
            A list of asset type group dictionaries.
        """
        return await super().get_request(
            endpoint="asset_type_groups",
            response_key="asset_type_groups",
            cls=AssetTypeGroup,
            **kwargs,
        )

    async def get_item_types(self, **kwargs):
        """Gets all item types.

        Returns all item types, can be filtered by various keywords:

        Args:
            item_type_id (str): Item type GUID.
            parameter_type_id (str): Parameter type GUID.
            asset_type_id (str): Asset type GUID.

        Returns:
            List of item type dictionaries.
        """
        return await super().get_request(
            endpoint="item_types",
            response_key="item_types",
            cls=ItemType,
            **kwargs,
        )

    async def get_units(self, **kwargs):
        """Gets all units.

        Returns all units, can be filtered to those associated with a given parameter type:

        Args:
            parameter_type_id (str): Parameter type GUID.

        Returns:
            List of unit dictionaries.
        """
        return await super().get_request(
            endpoint="units", response_key="units", cls=Unit, **kwargs
        )

    async def get_unit_types(self, **kwargs):
        """Gets all unit types.

        Returns:
            List of unit type dictionaries.
        """
        return await super().get_request(
            endpoint="unit_types", response_key="unit_types", cls=UnitType, **kwargs
        )

    async def get_unit_systems(self, **kwargs):
        """Gets all unit systems.

        Returns:
            List of item type dictionaries.
        """
        return await super().get_request(
            endpoint="unit_systems",
            response_key="unit_systems",
            cls=UnitSystem,
            **kwargs,
        )

    async def get_tags(self, **kwargs):
        """Gets all tags.

        Returns all tags, can be filtered by tag type:

        Args:
            tag_type_id (str): Tag type GUID.

        Returns:
            List of tag type dictionaries.
        """
        return await super().get_request(
            endpoint="tags", response_key="tags", cls=Tag, **kwargs
        )

    async def get_tag_types(self, **kwargs):
        """Gets all tag types.

        Returns:
            List of tag type dictionaries.
        """
        return await super().get_request(
            endpoint="tag_types", response_key="tag_types", cls=TagType, **kwargs
        )


class UnitSystem(BaseModel):
    id: str
    name: str
    short_name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]


class Unit(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    unit_type_id: Optional[str]
    unit_system_id: Optional[str]


class AssetTypeGroup(BaseModel):
    id: str
    name: str

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")


class AssetType(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    asset_sub_type: Optional[bool]
    deleted_at: Optional[str]
    asset_type_group: Optional[AssetTypeGroup]
    parent_id: Optional[str]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")


class AssetSubType(BaseModel):
    id: str
    name: str
    parent_asset_sub_type_id: Optional[str]


class SourceType(BaseModel):
    id: str
    name: str
    visible: bool
    deleted_at: Optional[str]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")


class Asset(DDBClient):
    id: str
    name: str
    project_id: str
    parent: Optional[str]
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    asset_sub_type: Optional[Union[Optional[bool], AssetSubType]] = None
    asset_type_group: Optional[AssetTypeGroup] = None
    children: List[str]
    asset_type: Optional[AssetType]

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}, ID: {self.id}")

    def __eq__(self, other):
        if isinstance(other, Asset):
            if other.id == self.id:
                return True
            else:
                return False
        elif isinstance(other, NewAsset):
            if (
                other.parent == self.parent
                and other.asset_type == self.asset_type
                and other.name == self.name
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError

    async def get_assets(self, **kwargs):
        return await super().get_assets(parent_id=[self.id], **kwargs)

    async def get_parameters(self, **kwargs):
        return await super().get_parameters(asset_id=self.id, **kwargs)

    async def post_sources(self, sources: List["NewSource"]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)

    async def post_assets(
        self,
        assets: List["NewAsset"],
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

    async def post_parameters(self, parameters: List["NewParameter"]):
        """Posts a list of NewParameter objects to this asset.

        Args:
            parameters (List[NewParameter]): a list of NewParameter objects

        Returns:
            TODO:
        """
        for parameter in parameters:
            parameter.parent = self
        return await super().post_parameters(parameters)

    async def post_new_revision(self, parameter: "NewParameter"):

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

    async def post_new_revisions(self, parameters: List["NewParameter"]):
        return await asyncio.gather(
            *[self.post_new_revision(parameter=parameter) for parameter in parameters]
        )


class UnitType(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str


class ParameterType(BaseModel):
    id: str
    name: str
    data_type: str
    created_at: Optional[str]
    updated_at: Optional[str]
    global_parameter: bool
    deleted_at: Optional[str]
    default_unit: Optional[Unit]
    units: Optional[List[Unit]]
    unit_type: Optional[UnitType]

    def __repr__(self) -> str:
        return repr("Name: " + self.name + ", Data type: " + self.data_type)


class Source(BaseModel):
    id: str
    name: Optional[str] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    visible: Optional[bool] = None
    time: Optional[str] = None
    date_day: Optional[Optional[str]] = None
    date_month: Optional[Optional[str]] = None
    date_year: Optional[Optional[str]] = None
    reference: Optional[str] = None
    reference_id: Optional[str] = None
    reference_table: Optional[str] = None
    reference_url: Optional[str] = None
    scope: Optional[Optional[str]] = None
    title: Optional[str] = None
    url: Optional[Optional[str]] = None
    source_type: Optional[SourceType] = None

    def __repr__(self) -> str:
        return repr(f"Title: {self.title}, reference: {self.reference}, id: {self.id}")

    def __eq__(self, other):
        if isinstance(other, Source):
            if other.id == self.id:
                return True
            else:
                return False
        elif isinstance(other, NewSource):
            if (
                other.title == self.title
                and other.reference == self.reference
                and other.source_type == self.source_type
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError


class Value(BaseModel):
    id: Optional[str]
    value: Union[float, str, bool, None]
    unit: Optional[Unit]


class Staff(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    company_centre_arup_unit: str
    location_name: str
    grade_level: int
    my_people_page_url: str

    def __repr__(self) -> str:
        return repr(f"Name: {self.staff_name}")


class Revision(BaseModel):
    id: str
    status: str
    source: Source
    comment: Optional[str]
    location_in_source: Optional[str]
    values: List[Value]
    created_at: str
    created_by: Staff

    def __repr__(self) -> str:
        return repr(
            f"Value: {self.values}, Created by: {self.created_by.staff_name}, Status: {self.status}, Source: {self.source.title} - {self.source.reference}"
        )

    def __eq__(self, other):
        if isinstance(other, Revision):
            if other.id == self.id:
                return True
            else:
                return False
        elif isinstance(other, NewRevision):
            if (
                str(other.value) == str(self.values[0].value)
                and other.unit == self.values[0].unit
                and other.source == self.source
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError


class Parameter(BaseModel):
    id: str
    created_at: str
    project_id: str
    created_by: str
    parameter_type: ParameterType
    parents: Optional[List[Asset]]
    revision: Optional[Revision]
    deleted_at: Optional[str]

    def __eq__(self, other):
        if isinstance(other, Parameter):
            if other.id == self.id:
                return True
            else:
                return False
        elif isinstance(other, NewParameter):
            if (
                other.parameter_type == self.parameter_type
                and other.revision == self.revision
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError


class ItemType(BaseModel):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]
    parameter_type: ParameterType
    asset_type: Optional[AssetType]
    created_by: Staff
    updated_by: Staff


class Project(DDBClient):
    centre_code: str
    job_number: str
    job_name_short: str
    organisation_name: Optional[str]
    project_director_name: Optional[str]
    project_manager_name: Optional[str]
    project_url: str
    scope_of_works: Optional[str]
    project_manager_email: Optional[str]
    project_director_email: Optional[str]
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

    async def post_sources(self, sources: List["NewSource"]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)

    async def post_parameters(
        self,
        parameters: List["NewParameter"],
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

    async def post_new_parameters(self, parameters: List["NewParameter"]):
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
        )
        if response.status == 400:
            res = await response.json()
            print(res["details"])
        return response

    async def post_new_revision(self, parameter: "NewParameter"):

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

    async def post_new_revisions(self, parameters: List["NewParameter"]):
        return await asyncio.gather(
            *[self.post_new_revision(parameter=parameter) for parameter in parameters]
        )

    async def post_assets(self, assets: List["NewAsset"]):
        return await super().post_assets(assets=assets)

    async def project_df_wip(self):
        return pd.DataFrame(
            [vars(parameter) for parameter in await self.get_parameters()],
            columns=[
                "parents_0_asset_type_name",
                "parents_0_name",
                "parents_0_id",
                "id",
                "parameter_type_name",
                "revision_values_0_value",
                "revision_values_0_unit_name",
                "revision_source_source_type_name",
                "revision_source_title",
                "revision_source_reference",
            ],
        )

        b = {
            "parents_0_asset_type_name": "Asset Type",
            "parents_0_name": "Asset Name",
            "parents_0_id": "Asset ID",
            "id": "Parameter ID",
            "parameter_type_name": "Parameter Type",
            "revision_values_0_value": "Value",
            "revision_values_0_unit_name": "Unit",
            "revision_source_source_type_name": "Source Type",
            "revision_source_title": "Source Title",
            "revision_source_reference": "Source Reference",
        }
        df_simple = df.copy()
        df_simple.rename(columns=b, inplace=True)

        return df_simple

    async def assets_df_wip(self):
        return pd.DataFrame(
            [vars(asset) for asset in await self.get_assets()],
            columns=["asset_type_name", "name", "id", "parent"],
        )

        b = {
            "asset_type_name": "Asset Type",
            "name": "Asset",
            "id": "Asset ID",
            "parent": "Parent Asset ID",
        }
        df_simple = df.copy()
        df_simple.rename(columns=b, inplace=True)

        return df_simple


class TagType(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]


class Tag(BaseModel):
    id: str
    name: str
    global_tag: bool
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    tag_type: TagType


class NewSource(BaseModel):
    source_type: SourceType
    title: str
    reference: str
    url: Optional[str]
    day: Optional[str] = "1"
    month: Optional[str] = "1"
    year: Optional[str] = "2001"

    def __eq__(self, other):
        if isinstance(other, NewSource) or isinstance(other, Source):

            if (
                other.title == self.title
                and other.reference == self.reference
                and other.source_type == self.source_type
            ):

                return True
            else:
                return False
        else:
            raise NotImplementedError


class NewRevision(BaseModel):

    value: Union[str, int, float, bool]
    unit: Optional[Unit]
    source: Union[Source, NewSource]
    comment: str = "Empty"
    location_in_source: str = "Empty"

    def __eq__(self, other):
        if isinstance(other, NewRevision):
            if (
                other.value == self.value
                and other.unit == self.unit
                and other.source == self.source
            ):
                return True
            else:
                return False
        elif isinstance(other, Revision):
            if (
                str(other.values[0].value) == str(self.value)
                and other.values[0].unit == self.unit
                and other.source == self.source
            ):
                return True
            else:
                return False

        else:
            raise NotImplementedError


class NewParameter(BaseModel):
    id: Optional[str]
    parameter_type: ParameterType
    revision: Optional[NewRevision]
    parent: Asset

    def __eq__(self, other):
        if isinstance(other, Parameter) or isinstance(other, NewParameter):
            if (
                other.parameter_type == self.parameter_type
                and other.revision == self.revision
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError


class NewAsset(BaseModel):
    id = str(uuid4())
    asset_type: AssetType
    name: str
    parent: Optional[Union[Asset, "NewAsset"]]

    def __eq__(self, other):
        if isinstance(other, Asset) or isinstance(other, NewAsset):
            if (
                other.parent == self.parent
                and other.asset_type == self.asset_type
                and other.name == self.name
            ):
                return True
            else:
                return False
        else:
            raise NotImplementedError
