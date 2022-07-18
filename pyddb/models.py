import asyncio
from enum import Enum
from typing import Any, List, Optional, Type, Union
from uuid import UUID, uuid4
import aiohttp
import pandas as pd
from DDBpy_auth import DDBAuth
from pydantic import BaseModel, Field


def split_list(list_a, chunk_size):

    for i in range(0, len(list_a), chunk_size):
        yield list_a[i : i + chunk_size]


class BaseURL(str, Enum):
    """ "Base URLs corresponding to DDB environments. Using an Enum instead
    of a dictionary to help with auto-completion and avoid magic strings."""

    prod = "https://ddb.arup.com/api/"
    dev = "https://dev.ddb.arup.com/api/"
    sandbox = "https://sandbox.ddb.arup.com/api/"


def generate_payload(**kwargs):
    """Generates a dictionary of provided keywords and values."""
    return dict(kwargs.items())


class DDB(BaseModel):
    url: Optional[str]
    headers = {
        "Authorization": "Bearer " + DDBAuth().acquire_new_access_content(),
        "version": "0",
    }

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
        try:
            return [cls.parse_obj(x) for x in result[response_key]]
        except KeyError:
            return []

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
        assets = await self.get_request(
            endpoint="assets", response_key="assets", cls=Asset, **kwargs
        )
        for asset in assets:
            setattr(asset, "url", self.url)
        return assets

    async def post_sources(self, sources: List["NewSource"], reference_id: str):
        source_bodies = []
        existing_sources_to_return = []
        results = None
        existing_sources = await self.get_sources(
            reference_id=reference_id,
            source_type_id=list({source.source_type.id for source in sources}),
            title=list({source.title for source in sources}),
            reference=list({source.reference for source in sources}),
        )

        for source in sources:

            if source in existing_sources:
                existing_sources_to_return.append(
                    next(s for s in existing_sources if s == source)
                )
            else:
                body = {
                    "source_type_id": source.source_type.id,
                    "title": source.title,
                    "reference": source.reference,
                    "reference_id": reference_id,
                    "reference_table": "projects",
                    "reference_url": "https://ddb.arup.com/project",
                }
                source_bodies.append(body)

        if source_bodies != []:
            async with aiohttp.ClientSession() as session:
                responses = await asyncio.gather(
                    *[
                        session.post(
                            f"{self.url}sources",
                            json=source_body,
                            headers=self.headers,
                            ssl=False,
                        )
                        for source_body in source_bodies
                    ]
                )
                results = await asyncio.gather(
                    *[response.json() for response in responses]
                )
        if results:
            existing_sources_to_return += [
                Source(**result["source"]) for result in results
            ]
        return existing_sources_to_return

    # async def post_sources(self, sources: List["NewSource"], reference_id: str):

    #     return await asyncio.gather(
    #         *[
    #             self.post_source(source=source, reference_id=reference_id)
    #             for source in sources
    #         ]
    #     )

    async def handle_post_assets(
        self,
        project: "Project",
        assets: List["NewAsset"],
    ):
        body = {"assets": []}

        for asset in assets:
            asset_body = {
                "asset_id": str(asset.id),
                "asset_type_id": asset.asset_type.id,
                "project_id": project.project_id,
                "name": asset.name,
            }
            if asset.parent:
                asset_body["parent_id"] = str(asset.parent.id)
            body["assets"].append(asset_body)

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
            elif response.status == 422:
                existing_assets = await project.get_assets(
                    asset_type_id=list({a.asset_type.id for a in assets})
                )

                returned_assets = []
                for new_asset in assets:
                    returned_assets.extend(
                        asset for asset in existing_assets if asset == new_asset
                    )

                return returned_assets
            else:
                print("Error posting assets")

                print(response.status)
                print(body)
                return []

    async def post_assets(self, project: "Project", assets: List["NewAsset"]):
        # ddb = DDB(url=BaseURL.sandbox)

        # sort assets into hierarchy order
        # asset_types = await ddb.get_asset_types()
        # asset_types_order = [a.name for a in asset_types]

        asset_types_order = [
            "site",
            "building",
            "space type",
            "space instance",
            "building system",
            "building envelope",
            "network link",
            "network asset",
            "masterplanning site",
            "plot",
            "equipment type",
            "equipment sub type",
            "area",
            "ground model",
            "layer",
            "case",
            "assembly",
            "2nd level sub component",
            "3rd level sub component",
            "bridge components",
            "vehicles",
            "railway",
            "track type",
            "wire run",
            "overhead line engineering",
            "bed formation",
            "span",
            "in span equipment",
            "material",
            "bridge",
            "deck/support/non structural elements",
            "span/support/ancillary",
            "network asset element instance",
            "network asset element type",
            "track sub type",
            "network asset component",
            "building element instance",
            "bridge element type",
            "sub system",
            "network asset sub element type",
            "bridge component name",
            "network asset system",
            "network asset alignment",
            "building sub frame material",
            "building envelope material",
            "building element sub type",
            "track alignment",
            "building envelope component",
            "building sub frame",
            "network asset sub element instance",
            "building frame",
            "masterplanning area",
            "product type",
            "generic",
            "product",
            "system group",
            "building envelope system",
            "network asset frame",
            "network asset sub component",
            "building element type",
            "bridge component element",
            "network asset element sub type",
            "bridge panel",
        ]

        sorted_new_assets = sorted(
            assets,
            key=lambda x: asset_types_order.index(x.asset_type.name),
            reverse=False,
        )

        existing_assets = await project.get_assets()
        new_assets = []
        returned_assets = []

        for asset in sorted_new_assets:
            if isinstance(asset.parent, Asset) or asset.parent is None:
                for existing_asset in existing_assets:

                    if existing_asset.__eq__(asset):
                        this_existing_asset = next(
                            a for a in existing_assets if a == asset
                        )
                        returned_assets.append(this_existing_asset)
                        for child in sorted_new_assets:
                            if child.parent and child.parent.id == asset.id:
                                child.parent = this_existing_asset

            new_assets.append(
                NewAsset(
                    id=str(asset.id),
                    asset_type=asset.asset_type,
                    name=asset.name,
                    parent=asset.parent,
                )
            )

        if new_assets != []:
            returned_assets += await self.handle_post_assets(
                project=project, assets=new_assets
            )
        return returned_assets

    async def post_parameters(
        self, project: "Project", parameters: List["NewParameter"]
    ):

        # Wow this entire function is just awful
        project_parameters = await project.get_parameters(
            page_limit=99999,
            parameter_type_id=[p.parameter_type.id for p in parameters],
        )
        existing_parameters = [
            (p.parameter_type.id, p.parents[0].id if p.parents else None)
            for p in project_parameters
        ]
        existing_revisions = [
            (p.parameter_type.id, p.parents[0].id if p.parents else None, p.revision)
            for p in project_parameters
        ]
        new_parameters = []
        new_revisions = []
        for parameter in parameters:
            if (
                parameter.parameter_type.id,
                parameter.parent.id if parameter.parent else None,
            ) in existing_parameters:

                if (
                    parameter.parameter_type.id,
                    parameter.parent.id if parameter.parent else None,
                    parameter.revision or None,
                ) in existing_revisions:
                    continue
                if parameter.parent:
                    setattr(
                        parameter,
                        "id",
                        next(
                            p.id
                            for p in [x for x in project_parameters if x.parents != []]
                            if p.parameter_type.id == parameter.parameter_type.id
                            and p.parents[0].id == parameter.parent.id
                        ),
                    )

                else:
                    setattr(
                        parameter,
                        "id",
                        next(
                            p.id
                            for p in project_parameters
                            if p.parameter_type.id == parameter.parameter_type.id
                            and not p.parents
                        ),
                    )

                new_revisions.append(parameter)
            else:

                new_parameters.append(parameter)

        await asyncio.gather(
            self.post_new_parameters(project=project, parameters=new_parameters),
            self.post_new_revisions(parameters=new_revisions),
        )

    async def post_new_parameters(
        self,
        project: "Project",
        parameters: List["NewParameter"],
    ):

        new_parameters = []

        for parameter in parameters:
            parameter_body = (
                {
                    "parameter_type_id": parameter.parameter_type.id,
                    "project_id": project.project_id,
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
                if parameter.revision
                else {
                    "parameter_type_id": parameter.parameter_type.id,
                    "project_id": project.project_id,
                }
            )

            if parameter.parent:
                parameter_body["parent_ids"] = str(parameter.parent.id)
            new_parameters.append(parameter_body)

        if new_parameters != []:
            parameter_lists = list(split_list(new_parameters, 40))
            tasks = []
            for parameter_list in parameter_lists:
                body = {"parameters": parameter_list}
                tasks.append(
                    self.post_request(
                        endpoint="parameters",
                        body=body,
                    )
                )

            responses = await asyncio.gather(*tasks)
            for response in responses:

                if response.status == 400:
                    print("400 Error")
                    # res = await response.json()
                if response.status == 500:
                    print("500 Error")
                    # res = await response.json()
            return responses
        return None

    async def post_new_revisions(self, parameters: List["NewParameter"]):
        revision_bodies = {
            parameter.id: {
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
            for parameter in parameters
        }

        async with aiohttp.ClientSession() as session:

            responses = await asyncio.gather(
                *[
                    session.post(
                        f"{self.url}parameters/{parameter_id}/revision",
                        json=revision_body,
                        headers=self.headers,
                        ssl=False,
                    )
                    for parameter_id, revision_body in revision_bodies.items()
                ]
            )

            # return await response.json()

    # async def post_new_revisions(self, parameters: List["NewParameter"]):
    #     return await asyncio.gather(
    #         *[self.post_new_revision(parameter=parameter) for parameter in parameters]
    #     )

    async def post_tag(self, tag: "Tag"):
        if isinstance(self, Project):
            body = {
                "reference_id": self.project_id,
                "reference_table": "projects",
                "reference_url": f"{self.url}projects",
            }
        if isinstance(self, Parameter):
            body = {
                "reference_id": self.id,
                "reference_table": "parameters",
                "reference_url": f"{self.url}parameters",
            }
        if isinstance(self, Asset):
            body = {
                "reference_id": self.id,
                "reference_table": "assets",
                "reference_url": f"{self.url}assets",
            }
        await self.post_request(endpoint=f"tags/{tag.id}/links", body=body)

    async def get_projects(self, **kwargs):
        """Returns a list of project objects.

        Returns:
            List of project dictionaries.
        """
        projects = await self.get_request(
            endpoint="projects", response_key="projects", cls=Project, **kwargs
        )
        for project in projects:
            setattr(project, "url", self.url)
        return projects

    async def post_project(self, project_number: str, confidential: bool = False):
        body = {"number": project_number, "confidential": confidential}
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
        projects = Project(**result["project"])
        for project in projects:
            setattr(project, "url", self.url)
        return projects

    async def get_source_types(self, **kwargs):
        """Retreives list of source types objects."""
        return await self.get_request(
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
        return await self.get_request(
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
        return await self.get_request(
            endpoint="asset_types", response_key="asset_types", cls=AssetType, **kwargs
        )

    async def get_asset_type_groups(self, **kwargs):
        """Returns all asset type groups.

        Args:
            asset_type_group_id (str): Asset type group GUID.

        Returns:
            A list of asset type group dictionaries.
        """
        return await self.get_request(
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
        return await self.get_request(
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
        return await self.get_request(
            endpoint="units", response_key="units", cls=Unit, **kwargs
        )

    async def get_unit_types(self, **kwargs):
        """Gets all unit types.

        Returns:
            List of unit type dictionaries.
        """
        return await self.get_request(
            endpoint="unit_types", response_key="unit_types", cls=UnitType, **kwargs
        )

    async def get_unit_systems(self, **kwargs):
        """Gets all unit systems.

        Returns:
            List of item type dictionaries.
        """
        return await self.get_request(
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
        return await self.get_request(
            endpoint="tags", response_key="tags", cls=Tag, **kwargs
        )

    async def get_tag_types(self, **kwargs):
        """Gets all tag types.

        Returns:
            List of tag type dictionaries.
        """
        return await self.get_request(
            endpoint="tag_types", response_key="tag_types", cls=TagType, **kwargs
        )


class UnitSystem(BaseModel):
    id: str
    name: str
    short_name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class Unit(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]
    unit_type_id: Optional[str]
    unit_system_id: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class AssetTypeGroup(BaseModel):
    id: str
    name: str

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class AssetType(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    asset_sub_type: Optional[bool]
    deleted_at: Optional[str]
    asset_type_group: Optional[AssetTypeGroup]
    parent_id: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class AssetSubType(BaseModel):
    id: str
    name: str
    parent_asset_sub_type_id: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class SourceType(BaseModel):
    id: str
    name: str
    visible: bool
    deleted_at: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class Asset(DDB):
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

    def __str__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}, ID: {self.id}")

    def __eq__(self, other):
        if isinstance(other, Asset) and other.id == self.id:
            return True
        elif (
            isinstance(other, Asset)
            or not isinstance(other, NewAsset)
            and other == None
        ):
            return False
        elif isinstance(other, NewAsset):
            other_parent = other.parent.id if other.parent else other.parent
            return (
                other_parent == self.parent
                and other.asset_type == self.asset_type
                and other.name == self.name
            )

        else:
            print(type(other).__name__)
            raise NotImplementedError

    async def get_assets(self, **kwargs):
        return await super().get_assets(parent_id=[self.id], **kwargs)

    async def get_parameters(self, **kwargs):
        return await super().get_parameters(asset_id=self.id, **kwargs)

    async def post_sources(self, sources: List["NewSource"]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)


class UnitType(BaseModel):
    id: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


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

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(
            f"Name: {self.name}, Data Type: {self.data_type}, ID: {self.id}, Unit Type:{self.unit_type or None}"
        )

    def __eq__(self, other):
        if isinstance(other, ParameterType):
            return other.id == self.id
        else:
            raise NotImplementedError


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
    source_type_id: Optional[str] = None

    def __str__(self) -> str:
        return str(
            f"Title: {self.title}, Reference: {self.reference}, Source Type: {self.source_type.name}"
        )

    def __repr__(self) -> str:
        return repr(f"Title: {self.title}, Reference: {self.reference}, ID: {self.id}")

    def __eq__(self, other):
        if isinstance(other, Source):
            return other.id == self.id
        elif isinstance(other, NewSource):
            return (
                other.title == self.title
                and other.reference == self.reference
                and other.source_type.id == self.source_type_id
            )

        else:
            raise NotImplementedError


class Value(BaseModel):
    id: Optional[str]
    value: Any  # Union[float, bool, str, None]
    unit: Optional[Unit]

    def __str__(self) -> str:
        return str(f"Value: {self.value}, Unit: {self.unit or None}")

    def __repr__(self) -> str:
        return repr(f"Value: {self.value}, Unit: {self.unit or None}, ID: {self.id}")


class Staff(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    company_centre_arup_unit: str
    location_name: str
    grade_level: Optional[int]
    my_people_page_url: str

    def __str__(self) -> str:
        return str(f"Name: {self.staff_name}")

    def __repr__(self) -> str:
        return repr(
            f"Name: {self.staff_name}, ID: {self.staff_id}, Email: {self.email}"
        )


class Revision(BaseModel):
    id: str
    status: str
    source: Source
    comment: Optional[str]
    location_in_source: Optional[str]
    values: List[Value]
    created_at: str
    created_by: Staff

    def __str__(self) -> str:
        return str(
            f"Value: {self.values[0].__str__()}, Source: {self.source.__str__()}, Status: {self.status}"
        )

    def __repr__(self) -> str:
        return repr(
            f"Value: {self.values[0].__repr__()}, Source: {self.source.__repr__()}, Status: {self.status}, ID: {self.id}"
        )

    def __eq__(self, other):
        if isinstance(other, Revision):
            return other.id == self.id
        elif isinstance(other, NewRevision):
            return (
                str(other.value) == str(self.values[0].value)
                and other.unit == self.values[0].unit
                and other.source == self.source
            )

        elif other is None:
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

    def __str__(self) -> str:
        return str(
            f"Parameter Type: {self.parameter_type}, Revision: {self.revision.__str__() if self.revision else None}"
        )

    def __repr__(self) -> str:
        return repr(
            f"Parameter Type: {self.parameter_type}, Revision: {self.revision.__repr__() if self.revision else None}, ID: {self.id}"
        )

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return other.id == self.id
        elif isinstance(other, NewParameter):
            return (
                other.parameter_type == self.parameter_type
                and other.revision == self.revision
            )

        else:
            raise NotImplementedError


class ItemType(BaseModel):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]
    parameter_type: ParameterType
    asset_type: Optional[AssetType]
    asset_sub_type: Optional[AssetSubType]
    created_by: Staff
    updated_by: Staff

    def __str__(self) -> str:
        return str(
            f"Parameter Type: {self.parameter_type.name}, Asset Type: {self.asset_type}"
        )

    def __repr__(self) -> str:
        return repr(
            f"Parameter Type: {self.parameter_type.name}, Asset Type: {self.asset_type}, ID: {self.id}"
        )


class Project(DDB):
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

    def __str__(self) -> str:
        return str(f"Name: {self.job_name_short}, Project Number: {self.project_code}")

    def __repr__(self) -> str:
        return repr(
            f"Name: {self.job_name_short}, Project Number: {self.project_code}, ID: {self.project_id}"
        )

    async def get_assets(self, **kwargs):
        return await super().get_assets(project_id=self.project_id, **kwargs)

    async def get_parameters(self, **kwargs):
        return await super().get_parameters(project_id=self.project_id, **kwargs)

    async def post_sources(self, sources: List["NewSource"]):

        return await super().post_sources(sources=sources, reference_id=self.project_id)

    async def post_new_parameters(self, parameters: List["NewParameter"]):
        return await super().post_new_parameters(project=self, parameters=parameters)

    async def post_assets(self, assets: List["NewAsset"]):
        return await super().post_assets(project=self, assets=assets)

    async def delete(self):
        async with aiohttp.ClientSession() as session:
            return await session.delete(
                f"{self.url}projects/{self.project_id}",
                headers=self.headers,
                ssl=False,
            )


class TagType(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]

    def __str__(self) -> str:
        return str(f"Name: {self.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, ID: {self.id}")


class Tag(BaseModel):
    id: str
    name: str
    global_tag: bool
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    tag_type: TagType

    def __str__(self) -> str:
        return str(f"Name: {self.name}, Tag Type: {self.tag_type}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, Tag Type: {self.tag_type}, ID: {self.id}")


class NewSource(BaseModel):
    source_type: SourceType
    title: str
    reference: str
    url: Optional[str]
    day: Optional[str] = "1"
    month: Optional[str] = "1"
    year: Optional[str] = "2001"

    def __str__(self) -> str:
        return str(
            f"Title: {self.title}, Reference: {self.reference}, Source Type: {self.source_type.name}"
        )

    def __repr__(self) -> str:
        return repr(
            f"Title: {self.title}, Reference: {self.reference}, Source Type: {self.source_type.name}"
        )

    def __eq__(self, other):
        if isinstance(other, (NewSource, Source)):

            return (
                other.title == self.title
                and other.reference == self.reference
                and other.source_type == self.source_type
            )

        else:
            raise NotImplementedError


class NewRevision(BaseModel):

    value: Union[str, int, float, bool]
    unit: Optional[Unit]
    source: Union[Source, NewSource]
    comment: str = "Empty"
    location_in_source: str = "Empty"

    def __str__(self) -> str:
        return str(f"Value: {self.value}, Source: {self.source.__str__()}")

    def __repr__(self) -> str:
        return repr(f"Value: {self.value}, Source: {self.source.__repr__()}")

    def __eq__(self, other):
        if isinstance(other, NewRevision):
            return (
                other.value == self.value
                and other.unit == self.unit
                and other.source == self.source
            )

        elif isinstance(other, Revision):
            return (
                str(other.values[0].value) == str(self.value)
                and other.values[0].unit == self.unit
                and other.source == self.source
            )

        elif other == None:
            return False
        else:
            print(type(other).__name__)
            print(other)
            raise NotImplementedError


class NewAsset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    asset_type: AssetType
    name: str
    parent: Optional[Union[Asset, "NewAsset"]]

    def __str__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}")

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, Type: {self.asset_type.name}, ID: {self.id}")

    def __eq__(self, other):
        if isinstance(other, (Asset, NewAsset)):

            return (
                other.parent == self.parent
                and other.asset_type == self.asset_type
                and other.name == self.name
            )

        elif other == None:
            return False
        else:
            raise NotImplementedError


class NewParameter(BaseModel):
    id: Optional[str]
    parameter_type: ParameterType
    revision: Optional[NewRevision]
    parent: Optional[Union[Asset, "NewAsset"]]

    def __str__(self) -> str:
        return str(
            f"Parameter Type: {self.parameter_type}, Revision: {self.revision.__str__() if self.revision else None}"
        )

    def __repr__(self) -> str:
        return repr(
            f"Parameter Type: {self.parameter_type}, Revision: {self.revision.__repr__() if self.revision else None}"
        )

    def __eq__(self, other):
        if isinstance(other, (Parameter, NewParameter)):
            return (
                other.parameter_type == self.parameter_type
                and other.revision == self.revision
            )

        else:
            raise NotImplementedError
