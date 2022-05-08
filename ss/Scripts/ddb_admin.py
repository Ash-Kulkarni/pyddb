import requests
from DDBpy_auth import DDBAuth  # https://github.com/arup-group/ddbpy_auth
import json

bearerToken = "Bearer " + DDBAuth().acquire_new_access_content()
headers = {"Authorization": bearerToken, "version": "0"}


def ddb_site_wrapper(func):
    def wrapper(*args, **kwargs):
        url = servers[site]
        return func(url=url, *args, **kwargs)

    return wrapper


servers = {
    "prod": "https://ddb.arup.com/api/",
    "dev": "https://ddb-dev.arup.com/api/",
    "sandbox": "https://ddb-sandbox.arup.com/api/",
}


def convert_to_lists(*args):
    output = []
    for arg in args:
        output.append([arg]) if type(arg) != list else output.append(arg)
    return output


@ddb_site_wrapper
def post_body(endpoint: str, body: dict, url: str = None):
    return requests.post(f"{url}{endpoint}", json=body, headers=headers).json()


# Assets


def post_asset_type(
    asset_id: str,
    asset_name: str,
    parent_id: str,
    asset_sub_type: str,
    asset_type_group_id: str = None,
):
    body = {
        "asset_types": [
            {
                "id": asset_id,
                "name": asset_name,
                "parent": parent_id,
                "asset_sub_type": asset_sub_type,
            }
        ]
    }

    if asset_type_group_id:
        body["asset_type_group_id"] = asset_type_group_id
    res = post_body("asset_types", body=body)
    print(res)
    return res


@ddb_site_wrapper
def delete_asset(asset_id, url: str = None):

    return requests.delete(f"{url}assets/{asset_id}", headers=headers).json()


"""@ddb_site_wrapper
def patch_asset_type(asset_id:str, new_asset_name:str, url:str=None):
    body = {
        "name": new_asset_name
        }

    return patch(f"{url}assets/{asset_id}", json=body, headers=headers).json()"""


def post_asset_type_group(asset_type_group_id: str, asset_type_group_name: str):
    body = {
        "asset_type_groups": [
            {"id": asset_type_group_id, "name": asset_type_group_name}
        ]
    }
    res = post_body("asset_type_groups", body=body)
    print(res)
    return res


@ddb_site_wrapper
def post_asset_sub_type(
    asset_sub_type_id: str,
    asset_sub_type_name: str,
    asset_type_id: str,
    parent_asset_sub_type_id: str = None,
    url: str = None,
):
    body = {
        "asset_sub_types": [
            {
                "id": asset_sub_type_id,
                "name": asset_sub_type_name,
                "asset_type_id": asset_type_id,
            }
        ]
    }

    if parent_asset_sub_type_id:
        body["asset_sub_types"][0][
            "parent_asset_sub_type_id"
        ] = parent_asset_sub_type_id
    res = requests.post(
        f"{url}asset_types/{asset_type_id}/asset_sub_types", json=body, headers=headers
    ).json()
    print(res)
    return res


# Parameters


def post_parameter_type(
    parameter_name,
    data_type,
    default_unit_id,
    parameter_type_id,
    global_parameter="true",
):
    """Uploads parameter types."""
    body = {
        "parameter_types": [
            {
                "id": parameter_type_id,
                "name": parameter_name,
                "data_type": data_type,
                "default_unit_id": default_unit_id,
                "global_parameter": global_parameter,
            }
        ]
    }
    print(body)
    a = post_body("parameter_types", body=body)
    print(a)
    return a


def post_parameter_type(
    parameter_name: str or list,
    data_type: str or list,
    default_unit_id: str or list,
    parameter_type_id: str or list,
    global_parameter="true",
):
    """Bulk uploads parameter types."""

    parameter_name, data_type, default_unit_id, parameter_type_id = convert_to_lists(
        parameter_name, data_type, default_unit_id, parameter_type_id
    )

    l = range(len(parameter_type_id))

    # batch size for batched parameter upload is 10
    chunks = [l[i : i + 10] for i in range(0, len(l), 10)]
    errors = []
    for chunk in chunks:
        body = {"parameter_types": []}
        for i in chunk:
            i -= 1

            parameter_type = {
                "id": parameter_type_id[i],
                "name": parameter_name[i],
                "data_type": data_type[i],
                # "default_unit_id": default_unit_id[i],
                "global_parameter": "true",  # global_parameter,
            }
            if default_unit_id[i] == "":
                parameter_type["default_unit_id"] = None
            else:
                parameter_type["default_unit_id"] = default_unit_id[i]

            body["parameter_types"].append(parameter_type)
        res = post_body("parameter_types", body=body)

        if "msg" in res:
            errors.append(body)
    if errors:
        print(f"There were errors posting the following bodies: {errors}")
    return


@ddb_site_wrapper
def delete_parameter(parameter_id: str, url: str = None):
    return requests.delete(f"{url}parameters/{parameter_id}", headers=headers).json()


# Items


def post_item_type(
    id: str or list,
    parameter_type_id: str or list,
    asset_type_id: str or list = None,
):
    """Bulk uploads item types."""
    id, parameter_type_id, asset_type_id = convert_to_lists(
        id, parameter_type_id, asset_type_id
    )

    l = range(len(id))
    errors = []
    # batch size for batched item upload is 10
    chunks = [l[i : i + 10] for i in range(0, len(l), 10)]

    for chunk in chunks:
        body = {"item_types": []}
        for i in chunk:
            i -= 1

            item = {"id": id[i], "parameter_type_id": parameter_type_id[i]}

            if asset_type_id[i]:
                item["asset_type_id"] = asset_type_id[i]

            body["item_types"].append(item)

        res = post_body("item_types", body=body)
        if "msg" in res:
            errors.append(body)
    if errors:
        print(f"There were errors posting the following bodies: {errors}")
    return


# Units


def post_unit(unit_id: str, unit_name: str, unit_type_id: str, unit_system_id: str):
    errors = []
    body = {
        "units": [
            {
                "id": unit_id,
                "name": unit_name,
                "unit_type_id": unit_type_id,
                "unit_system_id": unit_system_id,
            }
        ]
    }

    res = post_body("units", body=body)
    if "msg" in res:
        errors.append(body)
    if errors:
        print(f"There were errors posting the following bodies: {errors}")
    return


def post_unit_type(unit_type_id: str, unit_type_name: str):
    errors = []
    body = {"unit_types": [{"id": unit_type_id, "name": unit_type_name}]}

    res = post_body("unit_types", body=body)
    if "msg" in res:
        errors.append(body)
    if errors:
        print(f"There were errors posting the following bodies: {errors}")
    return res


def post_unit_system():
    pass


# this is a bit dangerous, commented out, deletes all ties to a given list of tag ids
"""def delete_all_tag_links(tag_ids):
    for tag_id in tag_ids:
        a = requests.get(f"https://ddb-dev.arup.com/api/tags/{tag_id}/links", headers=headers).json()["tag_links"]
        reference_ids = [x["reference_id"] for x in a]
        for reference_id in reference_ids:
            requests.delete(f"https://ddb-dev.arup.com/api/tags/{tag_id}/links/{reference_id}", headers=headers)"""


@ddb_site_wrapper
def patch_parameter(
    parameter_type_id: str,
    default_unit_id: str = None,
    name: str = None,
    data_type: str = None,
    url=None,
):

    body = {}
    if default_unit_id:
        body["default_unit_id"] = default_unit_id
    if name:
        body["name"] = name
    if data_type:
        body["data_type"] = data_type
    print(body)
    return requests.patch(
        f"{url}parameter_types/{parameter_type_id}", json=body, headers=headers
    ).json()
