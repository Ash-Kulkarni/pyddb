import pickle
from typing import List
from pyddb import ParameterType, AssetType, SourceType, Unit, Tag


def read_data(filename):

    PIK = f"data/{filename}.dat"

    with open(PIK, "rb") as f:
        return pickle.load(f)


def get_parameter_types_by_name(names: List[str]) -> List[ParameterType]:
    data = read_data("parameter_types")
    return [next((x for x in data if x.name == name), None) for name in names]


def get_parameter_types_by_id(ids: List[str]) -> List[ParameterType]:
    data = read_data("parameter_types")
    return [next((x for x in data if x.id == id), None) for id in ids]


def get_asset_types_by_name(names: List[str]) -> List[AssetType]:
    data = read_data("asset_types")
    return [next((x for x in data if x.name == name), None) for name in names]


def get_asset_types_by_id(ids: List[str]) -> List[AssetType]:
    data = read_data("asset_types")
    return [next((x for x in data if x.id == id), None) for id in ids]


def get_source_types_by_name(names: List[str]) -> List[SourceType]:
    data = read_data("source_types")
    return [next((x for x in data if x.name == name), None) for name in names]


def get_source_types_by_id(ids: List[str]) -> List[SourceType]:
    data = read_data("source_types")
    return [next((x for x in data if x.id == id), None) for id in ids]


def get_units_by_name(names: List[str]) -> List[Unit]:
    data = read_data("units")
    return [next((x for x in data if x.name == name), None) for name in names]


def get_units_by_id(ids: List[str]) -> List[Unit]:
    data = read_data("units")
    return [next((x for x in data if x.id == id), None) for id in ids]


def get_tags_by_name(names: List[str]) -> List[Tag]:
    data = read_data("tags")
    return [next((x for x in data if x.name == name), None) for name in names]


def get_tags_by_id(ids: List[str]) -> List[Tag]:
    data = read_data("tags")
    return [next((x for x in data if x.id == id), None) for id in ids]


def get_parameter_type_by_name(name: str) -> ParameterType:
    data = read_data("parameter_types")
    return next((x for x in data if x.name == name), None)


def get_parameter_type_by_id(id: str) -> ParameterType:
    data = read_data("parameter_types")
    return next((x for x in data if x.id == id), None)


def get_asset_type_by_name(name: str) -> AssetType:
    data = read_data("asset_types")
    return next((x for x in data if x.name == name), None)


def get_asset_type_by_id(id: str) -> AssetType:
    data = read_data("asset_types")
    return next((x for x in data if x.id == id), None)


def get_source_type_by_name(name: str) -> SourceType:
    data = read_data("source_types")
    return next((x for x in data if x.name == name), None)


def get_source_type_by_id(id: str) -> SourceType:
    data = read_data("source_types")
    return next((x for x in data if x.id == id), None)


def get_unit_by_name(name: str) -> Unit:
    data = read_data("units")
    return next((x for x in data if x.name == name), None)


def get_unit_by_id(id: str) -> Unit:
    data = read_data("units")
    return next((x for x in data if x.id == id), None)


def get_tag_by_name(name: str) -> Tag:
    data = read_data("tags")
    return next((x for x in data if x.name == name), None)


def get_tag_by_id(id: str) -> Tag:
    data = read_data("tags")
    return next((x for x in data if x.id == id), None)
