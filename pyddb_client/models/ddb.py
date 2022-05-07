import aiohttp
import pyddb_client.models as models


class DDB(models.DDBClient):
    async def get_projects(self, **kwargs):
        """Returns a list of project objects.

        Returns:
            List of project dictionaries.
        """
        return await super().get_request(
            endpoint="projects", response_key="projects", cls=models.Project, **kwargs
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
        return models.Project(**result["project"])

    async def get_source_types(self, **kwargs):
        """Retreives list of source types objects."""
        return await super().get_request(
            endpoint="source_types",
            response_key="source_types",
            cls=models.SourceType,
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
            cls=models.ParameterType,
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
            endpoint="asset_types",
            response_key="asset_types",
            cls=models.AssetType,
            **kwargs,
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
            cls=models.AssetTypeGroup,
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
            cls=models.ItemType,
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
            endpoint="units", response_key="units", cls=models.Unit, **kwargs
        )

    async def get_unit_types(self, **kwargs):
        """Gets all unit types.

        Returns:
            List of unit type dictionaries.
        """
        return await super().get_request(
            endpoint="unit_types",
            response_key="unit_types",
            cls=models.UnitType,
            **kwargs,
        )

    async def get_unit_systems(self, **kwargs):
        """Gets all unit systems.

        Returns:
            List of item type dictionaries.
        """
        return await super().get_request(
            endpoint="unit_systems",
            response_key="unit_systems",
            cls=models.UnitSystem,
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
            endpoint="tags", response_key="tags", cls=models.Tag, **kwargs
        )

    async def get_tag_types(self, **kwargs):
        """Gets all tag types.

        Returns:
            List of tag type dictionaries.
        """
        return await super().get_request(
            endpoint="tag_types", response_key="tag_types", cls=models.TagType, **kwargs
        )

    async def get_asset_type_by_name(self, name: str):
        return next(
            (
                asset_type
                for asset_type in await self.get_asset_types()
                if asset_type.name == name
            ),
            None,
        )

    async def get_source_type_by_name(self, name: str):
        return next(
            (
                source_type
                for source_type in await self.get_source_types()
                if source_type.name == name
            ),
            None,
        )

    async def get_parameter_type_by_name(self, name: str):
        return next(
            (
                parameter_type
                for parameter_type in await self.get_parameter_types()
                if parameter_type.name == name
            ),
            None,
        )

    async def get_unit_by_name(self, name: str):
        return next(
            (unit for unit in await self.get_units() if unit.name == name),
            None,
        )
