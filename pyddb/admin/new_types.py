from typing import Optional, Union
from pydantic import BaseModel
from pyddb import (
    ParameterType,
    AssetType,
    AssetSubType,
    AssetTypeGroup,
    Unit,
    UnitSystem,
    UnitType,
)


class NewAssetType(BaseModel):
    id: str
    name: str
    parent: AssetType
    asset_sub_type: Optional[AssetSubType]
    asset_type_group_id: Optional[AssetTypeGroup]


class NewAssetTypeGroup(BaseModel):
    id: str
    name: str


class NewAssetSubtype(BaseModel):
    id: str
    name: str
    asset_type: AssetType
    parent_asset_sub_type: AssetSubType


class NewParameterType(BaseModel):
    name: str
    id: str
    data_type: str
    default_unit: Unit
    global_parameter: bool = True


class NewItemType(BaseModel):
    id: str
    parameter_type: Union[ParameterType, NewParameterType]
    asset_type: Optional[Union[AssetType, NewAssetType]]
    asset_sub_type: Optional[AssetSubType]


class NewUnit:
    id: str
    name: str
    unit_type: UnitType
    unit_system: UnitSystem


class NewUnitType:
    id: str
    name: str


class NewUnitSystem:
    pass
