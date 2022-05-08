"""Library for getting and posting values to the Digital Design Brief database.

Functions and classes to create and retreive projects, assets, parameters, and values.
"""
import requests
from DDBpy_auth import DDBAuth  # https://github.com/arup-group/ddbpy_auth
from pprint import pprint as pp
from typing import List

# import arupcomputepy
import json


bearerToken = "Bearer " + DDBAuth().acquire_new_access_content()
headers = {"Authorization": bearerToken, "version": "0"}
site = "dev"


def ddb_site_wrapper(func):
    """Wrapper function that builds endpoints for DDB environment."""

    def wrapper(*args, **kwargs):
        url = servers[site]
        return func(url=url, *args, **kwargs)

    return wrapper


servers = {
    "prod": "https://ddb.arup.com/api/",
    "dev": "https://dev.ddb.arup.com/api/",
    "sandbox": "https://sandbox.ddb.arup.com/api/",
}


def convert_to_lists(*args):
    """Converts all *args to lists."""
    output = []
    for arg in args:
        output.append([arg]) if type(arg) != list else output.append(arg)
    return output


def generate_payload(**kwargs):
    """Generates a dictionary of provided keywords and values."""
    return {key: value for (key, value) in kwargs.items()}


@ddb_site_wrapper
def get_all(endpoint: str, url: str = None, **kwargs):
    payload = generate_payload(**kwargs)
    return requests.get(f"{url}{endpoint}", params=payload, headers=headers).json()[
        endpoint
    ]


@ddb_site_wrapper
def post_body(endpoint: str, body: dict, url: str = None):
    return requests.post(f"{url}{endpoint}", json=body, headers=headers).json()


def flatten_data(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


# DesignCheck


def designcheck_calc(calc_id, job_number, variables):
    accessToken = arupcomputepy.AcquireNewAccessTokenDeviceFlow()

    if calc_id != "":
        response = arupcomputepy.MakeCalculationRequest(
            calcID=calc_id,
            jobNumber=job_number,
            accessToken=accessToken,
            isBatch=False,
            variables=variables,
            resultType="full",
        )

        designcheck_output = json.loads(response["output"])

        try:
            outputs = [
                [x["value"], x["units"], x["description"]]
                for x in designcheck_output["arupComputeResultItems"]
            ]

            values, units, source_references = [], [], []
            for output in outputs:
                values, units, source_references
                [
                    x.append(y)
                    for x, y in zip([values, units, source_references], output)
                ]
            return values, units, source_references

        except KeyError:
            errors = designcheck_output["errors"]
            error_str = "The DesignCheck2 calculation failed for the following reasons:"
            for i in errors:
                error_str += f"\n{i}"
            error_str += "\nPlease run again."
            return error_str


# Sources


def add_new_source(
    project_id: str,
    source_type_id: str or list,
    source_title: str or list,
    source_reference: str or list,
    source_url: str = None,
    source_day: str = None,
    source_month: str = None,
    source_year: str = None,
):
    """Posts new source(s) to a project.

    Posts new source(s) to the given project GUID.  Source type, title, and reference are mandatory.
    Source url and reference day, month, and year are optional.
    Lists of source information can be provided to post multiple sources.

    Args:
        project_id: Project GUID.
        source_type_id: Source type GUID.
        source_title: Source title.
        source_reference: Source reference.
        source_url: Source reference url.
        source_day: Source publication day.
        source_month: Source publication month.
        source_year: Source publication year.

    Returns:
        A list containing the source instance ID(s) in the order given.
    """
    (
        source_type_id,
        source_title,
        source_reference,
        source_url,
        source_day,
        source_month,
        source_year,
    ) = convert_to_lists(
        source_type_id,
        source_title,
        source_reference,
        source_url,
        source_day,
        source_month,
        source_year,
    )
    source_url = [None if x == "" else x for x in source_url]
    source_ids = []
    failed_sources = []

    existing_sources = get_sources(
        reference_id=project_id, page_limit=9999
    )  # get existing sources
    # print(existing_sources)
    for i, _ in enumerate(
        source_type_id
    ):  # for each new source, check if it already exists
        existing_source_ids = [
            existing_source["id"]
            for existing_source in existing_sources
            if existing_source["title"] == source_title[i]
            and existing_source["reference"] == source_reference[i]
            and existing_source["source_type"]["id"] == source_type_id[i]
            and existing_source["url"] == source_url[i]
        ]

        if existing_source_ids != []:
            source_ids.append(existing_source_ids[0])  # if it exists, find its id
        else:  # otherwise, post it and retreive its id

            source = {
                "source_type_id": source_type_id[i],
                "title": source_title[i],
                "reference": source_reference[i],
                "reference_id": project_id,
                "reference_table": "projects",
                "reference_url": "https://ddb.arup.com/project",
            }

            if source_url[i]:
                source["url"] = source_url[i]
            if source_day[i]:
                source["date_day"] = source_day[i]
            if source_month[i]:
                source["date_month"] = source_month[i]
            if source_year[i]:
                source["date_year"] = source_year[i]

            res = post_body(endpoint="sources/", body=source)

            if "details" in res:
                print(f"Error: {res['details']}")
                failed_sources.append(source)
            new_source_id = res["source"]["id"]
            # print("Source created successfully.")
            source_ids.append(new_source_id)
    # print(f"{len(source_ids)} source(s) located.")
    if failed_sources:
        print(
            f"The following ({len(failed_sources)}) sources failed: {pp(failed_sources)}"
        )
    return source_ids


def get_source_types(**kwargs):
    """Retreives JSON object of all source types."""

    return get_all(endpoint="source_types", **kwargs)


def get_sources(**kwargs):

    """Retreives JSON object of sources.

    Retrieves a JSON containing all sources in the DDB database.
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
    return get_all(endpoint="sources", **kwargs)


# Parameters


def add_new_parameters(
    parameter_type_id: str or list,
    project_id: str,
    asset_id: str = None,
    value: str or list = None,
    unit_id: str or list = None,
    source_id: str or list = None,
    batch_size: int = 20,
):
    """Posts new parameter, does not update/create new revision.
    Use add_update_parameter() instead.
    """

    parameter_type_id, value, unit_id, source_id = convert_to_lists(
        parameter_type_id, value, unit_id, source_id
    )

    l = range(len(parameter_type_id))

    # batch size for batched parameter upload is 12

    chunks = [l[i : i + batch_size] for i in range(0, len(l), batch_size)]

    if asset_id:
        p_ids = []
        for chunk in chunks:

            new_parameters = {"parameters": []}

            for i in chunk:

                i -= 1
                new_parameters["parameters"].append(
                    {
                        "parameter_type_id": parameter_type_id[i],
                        "project_id": project_id,
                        "parent_ids": asset_id,
                        "revision": {
                            "source_id": source_id[i],
                            "comment": "Python Upload",
                            "location_in_source": "Python",
                            "values": [{"value": value[i], "unit_id": unit_id[i]}],
                        },
                    }
                )
            a = post_body(endpoint="parameters/", body=new_parameters)

            if "details" in a:
                print(f"{a['details']}.")
                if "already exists" in a["details"]:
                    print("To update parameters, use a different function.")
                    return
                else:
                    return f"Error: {a['details']}."
            print(f"Parameter posted successfully.")
            # p_ids += [x["id"] for x in a["parameters"]]
            return

    else:
        p_ids = []
        for chunk in chunks:
            p_ids = []
            new_parameters = {"parameters": []}

            for i in chunk:

                i -= 1

                new_parameters["parameters"].append(
                    {
                        "parameter_type_id": parameter_type_id[i],
                        "project_id": project_id,
                        "revision": {
                            "source_id": source_id[i],
                            "comment": "Python Upload",
                            "location_in_source": "Python",
                            "values": [{"value": value[i], "unit_id": unit_id[i]}],
                        },
                    }
                )

            # a = requests.post(f"{url}parameters/", json=new_parameters, headers=headers).json()
            a = post_body(endpoint="parameters", body=new_parameters)

            if "details" in a:
                print(f"Error: {a['details']}.")
                if "already exists" in a["details"]:
                    return "To update parameters use a different function."
            if "details" in a:
                return f"Error: {a['details']}."

            p_ids += [x["id"] for x in a["parameters"]]

        if p_ids:
            print(f"Parameter posted successfully.")
            return p_ids
        else:
            print("No new parameters posted.")
            return


def update_parameters(
    parameter_id: str or list,
    value: str or list,
    unit_id: str or list,
    source_id: str or list,
):
    """Updates a given parameter.
    Use add_update_parameter() instead.
    """

    parameter_id, value, unit_id, source_id = convert_to_lists(
        parameter_id, value, unit_id, source_id
    )

    if parameter_id == []:  ## hack
        return
    # creates a dictionary of the existing value and source id for each parameter_id entered
    existing_parameters_dict = {
        id: {"value": value, "source": source}
        for (id, value, source) in [
            (
                x["id"],
                x["revision"]["values"][0]["value"],
                x["revision"]["source"]["id"],
            )
            for x in get_parameters(parameter_id=parameter_id)
        ]
    }
    for i, parameter_id in enumerate(parameter_id):

        # check if value or source have changed
        if (
            existing_parameters_dict[parameter_id]["value"] == value[i]
            and existing_parameters_dict[parameter_id]["source"] == source_id[i]
        ):
            continue

        updated_parameter = {
            "source_id": source_id[i],
            "values": [{"value": value[i], "unit_id": unit_id[i]}],
        }

        # response = requests.post(f"{url}parameters/" + parameter_id + "/revision", json=updated_parameter, headers=headers).json()
        response = post_body(
            endpoint=f"parameters/{parameter_id}/revision", body=updated_parameter
        )
        if "details" in response:
            print(f"Error: {response['details']}.")
            return
    return parameter_id


def get_parameter_id(
    parameter_type_id: str, asset_id: str = None, project_id: str = None
):
    """Gets a parameter ID from a parameter type id and an asset id/project id.

    Searches the supplied asset_id for the given parameter_type_id, and returns the parameter instance id.
    If no asset_id is provided, checks for a project_id instead.

    Args:
        parameter_type_id: Parameter type GUID.
        asset_id: Asset instance GUID.
        project_id: Project instance GUID.

    Returns:
        Parameter GUID.
    """
    if asset_id:
        return get_all(
            endpoint="parameters",
            asset_id=asset_id,
            parameter_type_id=parameter_type_id,
        )[0]["id"]
    elif project_id:
        return get_all(
            endpoint="parameters",
            project_id=project_id,
            project_parameter=True,
            parameter_type_id=parameter_type_id,
        )[0]["id"]
    else:
        print("Error in locating existing parameters.")


def get_parameter_types(**kwargs):
    """Retreives JSON object of parameter types.

    Returns a list of all parameter types, can be filtered by various keyword arguments:

    Args:
        **asset_type_id (str): Asset type GUID, will only return parameter_types available on the given asset_type.
        **not_asset_id (str): Asset instance GUID, will only return parameter_types that are not attached to the given asset_id.
        **not_project_id (str): Project instance GUID, will only return parameter_types that are not attached to the given project_id.

    Returns:
        List of parameter type dictionaries.
    """
    return get_all(endpoint="parameter_types", **kwargs)


def get_parameters(**kwargs):
    """Retreives JSON object of all parameters.

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
    return get_all(endpoint="parameters", **kwargs)


def check_parameter_exists(
    parameter_type_id: list, asset_id: str = None, project_id: str = None
):
    """Checks if parameter type exists on an asset or at project level.

    Checks if a parameter type instance exists on a specified asset instance.
    Checks project level on the given project_id if no asset_id is given.

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
        True or False
    """
    if asset_id:
        parameters = get_parameters(asset_id=asset_id)
    else:
        parameters = get_parameters(project_id=project_id, project_parameter=True)

    parameter_types = [x["parameter_type"]["id"] for x in parameters]

    return [True if x in parameter_types else False for x in parameter_type_id]


def add_update_parameter(
    parameter_type_id: str or list,
    project_id: str,
    asset_id: str = None,
    value: str or list = None,
    unit_id: list = None,
    source_id: str or list = None,
):
    """Posts a new parameter or a new entry for the existing one.

    Posts a given parameter to an asset_id, with the provided value, unit, and source.
    If it already exists and the value is different, creates a new revision instead.
    A list of types, values, units, and source ids can be provided to upload multiple values to a single asset.

    Args:
        parameter_type_id (str): Parameter type GUID
        project_id (str): Project instance GUID
        asset_id: str = Asset isntance GUID
        value (str): Parameter value
        unit_id (str): Unit GUID
        source_id (str): Source instance GUID
    """

    # check if exist
    parameter_type_id, value, unit_id, source_id = convert_to_lists(
        parameter_type_id, value, unit_id, source_id
    )
    if asset_id:
        parameter_exists_list = check_parameter_exists(
            asset_id=asset_id, parameter_type_id=parameter_type_id
        )
    else:
        parameter_exists_list = check_parameter_exists(
            project_id=project_id, parameter_type_id=parameter_type_id
        )

    new = {
        "parameter_type_id": [],
        "value": [],
        "unit_id": [],
        "source_id": [],
    }

    update = {
        "parameter_id": [],
        "value": [],
        "unit_id": [],
        "source_id": [],
    }

    for i, exist in enumerate(parameter_exists_list):
        if exist == False:

            new["parameter_type_id"].append(parameter_type_id[i])
            new["value"].append(value[i])
            new["unit_id"].append(unit_id[i])
            new["source_id"].append(source_id[i])

        else:
            update["value"].append(value[i])
            update["unit_id"].append(unit_id[i])
            update["source_id"].append(source_id[i])
            if asset_id:
                update["parameter_id"].append(
                    get_parameters(
                        asset_id=asset_id, parameter_type_id=parameter_type_id[i]
                    )[0]["id"]
                )
            else:
                update["parameter_id"].append(
                    get_parameters(
                        project_id=project_id,
                        parameter_type_id=parameter_type_id[i],
                        project_parameter=True,
                    )[0]["id"]
                )

    new_ids = add_new_parameters(
        new["parameter_type_id"],
        project_id,
        asset_id,
        new["value"],
        new["unit_id"],
        new["source_id"],
    )

    updated_ids = update_parameters(
        update["parameter_id"],
        update["value"],
        update["unit_id"],
        update["source_id"],
    )

    parameter_ids = []
    if new_ids:
        parameter_ids += list(new_ids)
    if updated_ids:
        parameter_ids += list(updated_ids)
    return  # parameter_ids


def get_parameter_value_from_id(parameter_id):
    """Returns the value of a given parameter_id.

    Args:
        parameter_id (str): Parameter instance GUID
    """
    return requests.get(endpoint="parameters", parameter_id=parameter_id)[0][
        "revision"
    ]["values"][0]["value"]


def get_parameter_values(asset_id: str, **kwargs):
    """Returns a dictionary of all parameter names and values on a given asset.

    Retreives all parameters on a given asset instance, can be filtered by various keywords.
    Response is converted into a dictionary of parameter names and values.

    Args:
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
        Dictionary of parameter names and values: {parameter_name: value}
    """
    parameters = get_parameters(asset_id=asset_id, **kwargs)

    names = [x["parameter_type"]["name"] for x in parameters]
    values = [x["revision"]["values"][0]["value"] for x in parameters]

    return {name: value for (name, value) in zip(names, values)}


def upload_parameters(
    project_id: str,
    asset_ids: List[str],
    parameter_type_ids: List[str],
    values: List[str],
    unit_ids: List[str],
    source_ids: List[str],
):
    existing_parameters = get_parameters(
        asset_id=asset_ids,
        project_id=project_id,
        # parameter_type_ids=parameter_type_ids,
        page_limit=9999,
    )

    existing_entries = [
        (
            x["id"],
            x["parents"][0]["id"],
            x["parameter_type"]["id"],
            x["revision"]["values"][0]["value"],
            x["revision"]["values"][0]["unit"],
            x["revision"]["source"]["id"],
        )
        for x in existing_parameters
    ]

    (
        existing_parameter_ids,
        existing_asset_ids,
        existing_parameter_type_ids,
        existing_values,
        existing_units,
        existing_source_ids,
    ) = list(map(list, zip(*existing_entries)))

    existing_unit_ids = [x if x is None else x["id"] for x in existing_units.copy()]

    parameter_id_map = {
        (parameter_type_id, asset_id): parameter_id
        for (parameter_type_id, asset_id, parameter_id) in list(
            zip(existing_parameter_type_ids, existing_asset_ids, existing_parameter_ids)
        )
    }

    existing_entries = list(
        map(
            list,
            zip(
                existing_asset_ids,
                existing_parameter_type_ids,
                existing_values,
                existing_unit_ids,
                existing_source_ids,
            ),
        )
    )
    entries = list(
        map(
            list,
            zip(
                asset_ids,
                parameter_type_ids,
                values,
                unit_ids,
                source_ids,
            ),
        )
    )
    new_parameters_list = []
    # updated_parameters_list = []
    ignored_parameters_list = []

    # sort into things that exist
    for i, entry in enumerate(entries.copy()):
        if entry in existing_entries:
            # entry is identical - update not required
            ignored_parameters_list.append(entry)
            continue
        elif entry[:2] in [x[:2] for x in existing_entries]:
            # parameter exists on asset, but value/unit/source is different
            # updated_parameters_list.append([existing_parameter_ids[i]] + entry)
            update_parameters(
                parameter_id=parameter_id_map[(entry[1], entry[0])],
                value=entry[2],
                unit_id=entry[3],
                source_id=entry[4],
            )
            # update parameter
        else:
            new_parameters_list.append(entry)
    new_parameters = {"parameters": []}
    for entry in new_parameters_list:

        new_parameter = {
            "parameter_type_id": entry[1],
            "project_id": project_id,
            "revision": {
                "source_id": entry[4],
                "comment": "Python Upload",
                "location_in_source": "Python Upload",
                "values": [
                    {
                        "value": entry[2],
                        "unit_id": None if entry[3] is None else entry[3],
                    }
                ],
            },
        }
        if entry[0]:
            new_parameter["parent_ids"] = entry[0]

        new_parameters["parameters"].append(new_parameter)

    num_new = len(new_parameters["parameters"])
    l = range(num_new)
    print(f"Posting {num_new} new parameter(s):")

    batch_size = 10
    chunks = [l[i : i + batch_size] for i in range(0, len(l), batch_size)]
    errors = []

    for i, chunk in enumerate(chunks):

        # quick fix for when body length == 1
        if len(new_parameters["parameters"]) > 1:
            body = {"parameters": []}
            batch = new_parameters["parameters"][list(chunk)[0] : list(chunk)[-1]]

            body["parameters"] = batch
        # quick fix for when body length == 1
        elif len(new_parameters["parameters"]) == 1:
            body = new_parameters

        if body != {"parameters": []}:
            res = post_body("parameters/", body=body)

            if "msg" in res:
                print(f"Errors in batch {i}.")
                errors.append(body)
            else:
                print(f"Batch {i+1} posted successfully.")
    if errors:
        print(
            f"There were errors posting the following ({len(errors)}) bodies: {errors}"
        )
    else:
        if num_new:
            print(f"All parameters posted successfully.")

    return


# Parameter Revisions


@ddb_site_wrapper
def get_all_revisions(parameter_id: str, url: str = None):
    """Returns all revisions for a given parameter_id.

    Args:
        parameter_id (str): Parameter instance GUID

    Returns:
        Dictionary of parameter revisions.
    """
    return requests.get(
        f"{url}parameters/{parameter_id}/revision", headers=headers
    ).json()


@ddb_site_wrapper
def patch_revision_status(
    parameter_id: str, new_status: str = None, comment: str = None, url: str = None
):
    """Updates a value's QA status.

    Updates status from answered to checked or checked to approved.
    The status can be reduced to any level below.
    Values can be rejected with a comment at any stage.

    Args:
        parameter_id (str): Parameter instance GUID
        new_status (str): New QA status, must be one of: "unanswered", "answered", "checked", "approved", or "rejected"
        comment (str): A comment about why the value was rejected.

    Returns:
        Revised parameter JSON.
    """
    s = ["answered", "checked", "approved", "rejected"]
    body = {}

    if new_status and new_status not in s:
        print(f"Revision status must be one of {s}")
    else:
        body["status"] = new_status
        if comment:
            body["comment"] = comment

    return requests.patch(
        f"{url}parameters/{parameter_id}/revision", json=body, headers=headers
    ).json()


# Projects


def add_new_project(job_number: str):
    """Posts a new project to DDB.

    Takes an 8 digit project number and posts the project to DDB.
    The project must exist in the Arup intranet.

    Args:
        job_number (str): 8 digit project number.

    Returns:
        The project instance GUID.
    """
    body = {"number": str(job_number)}

    res = post_body(endpoint="projects", body=body)

    if "projects" in res:
        print("Project created successfully.  Project ID retreived.")
        project_id = res["projects"][0]["project_id"]
        return project_id

    if "msg" in res:
        if res["msg"] == "Conflict":
            print("Existing Project Found.")
            return get_project_id(job_number)

    if "details" in res:
        print(f"Error: {res['details']}")
        return

    else:
        print("Unknown error.")
        return


def get_projects(**kwargs):
    """Gets all project instances.

    Returns:
        List of project dictionaries.
    """
    return get_all(endpoint="projects", **kwargs)


def get_project_id(job_number):
    """Gets a project instance GUID.

    Takes an 8 digit project number and retreives the project instance GUID.
    The project must exist in the Arup intranet.

    Args:
        job_number (str): 8 digit project number.

    Returns:
        The project instance GUID.
    """
    try:
        return get_all(endpoint="projects", number=job_number)[0]["project_id"]
    except IndexError:
        print("Project not found.")
        return


# Assets


def add_new_asset(
    asset_type_id: str, project_id: str, asset_name: str, parent_id: str = None
):
    """Adds a new asset to a project.

    Checks if the asset already exists, if it does, returns asset instance GUID.
    Otherwise, adds an asset of the given name and type below the parent_id given.

    Args:
        asset_type_id (str): Asset type GUID.
        project_id (str): Project instance GUID.
        asset_name (str): New asset instance name.
        parent_id (str): Parent asset instance GUID.

    Returns:
        Asset instance GUID
    """
    asset_id = check_asset_exists(project_id, asset_type_id, parent_id, asset_name)
    if asset_id == False:
        asset = {
            "assets": [
                {
                    "asset_type_id": asset_type_id,
                    "project_id": project_id,
                    "name": asset_name,
                }
            ]
        }

        if parent_id:
            asset["assets"][0]["parent_id"] = parent_id

        # a = requests.post(f"{url}assets", json=asset, headers=headers).json()
        a = post_body(endpoint="assets", body=asset)

        print(f"Asset: {asset_name} created successfully.")
        return a["assets"][0]["id"]
    else:
        print(f"Asset: {asset_name} already exists.")
        return asset_id


@ddb_site_wrapper
def check_asset_exists(
    project_id, asset_type_id, parent_id, asset_name, url: str = None
):
    """Checks if an asset exists.

    Checks if an asset of the given name and type exist under the given parent asset.
    If the parent_id is None, searches the whole project, used for level 0 assets.

    Args:
        project_id (str): Project instance GUID.
        asset_type_id (str): Asset type GUID of the asset you are checking for.
        parent_id (str): Parent asset instance GUID.
        asset_name (str): Name of the asset you are checking for.

    Returns:
        Asset instance GUID or False.
    """
    parent_query = f"&parent_id={parent_id}" if parent_id != None else ""

    a = requests.get(
        f"{url}assets?asset_type_id={asset_type_id}{parent_query}&project_id={project_id}&show_deleted_assets=false",
        headers=headers,
    ).json()

    if "details" in a:
        return f"Error: {a['details']}"
    if "msg" in a:
        return "Error: Check asset_type_id."
    b = [x["id"] for x in a["assets"] if x["name"] == asset_name]

    if b == []:
        return False
    else:
        return b[0]


def get_assets(**kwargs):
    """Gets all asset instances.

    Gets all assets from DDB, can be filtered by various keywords:

    Args:
        asset_id (str): Asset instance GUID.
        asset_type_id (str): Asset type GUID.
        parent_id (str): Parent asset instance GUID.
        project_id (str): Project instance GUID.

    Returns:
        List of asset dictionaries.
    """
    return get_all(endpoint="assets", **kwargs)


@ddb_site_wrapper
def get_descendants_of(asset_id: str, url: str = None):
    return requests.get(f"{url}assets/{asset_id}", headers=headers).json()


# returns the ordered hierarchies of given asset's parents
@ddb_site_wrapper
def get_hierarchy(asset_id: str, url: str = None):
    """Returns the ordered hierarchies of a given assets parents.

    Args:
        asset_id (str): Asset instance GUID.

    Returns:
        List of asset dictionaries of parent asset instances:

        [{
            "id": "933c36d0-8158-4d28-8c2d-319a33b92312",
            "name": "Wellington Place"
        },
        {
            "id": "62f3f99c-1bf5-4fd4-97e9-ef9f3af40879",
            "name": "4 Wellington Place"
        },
        {
            "id": "87a10e7a-a0b7-4fd1-b4b7-b2f5ffc128a0",
            "name": "Hot Water"
        }]
    """
    return requests.get(f"{url}assets/{asset_id}/hierarchy", headers=headers).json()[
        "hierarchies"
    ][0]


# Asset Types


def get_asset_types(**kwargs):
    """Returns all asset types.

    Response can be filtered by various keywords:

    Args:
        project_id (str): Project instance GUID.
        parent_asset_id (str): Parent asset instance GUID.
        asset_type_group_id (str): Asset type group GUID.

    Returns:
        A list of asset type dictionaries.
    """
    return get_all(endpoint="asset_types", **kwargs)


def get_asset_type_groups(**kwargs):
    """Returns all asset type groups.

    Args:
        asset_type_group_id (str): Asset type group GUID.

    Returns:
        A list of asset type group dictionaries.
    """
    return get_all(endpoint="asset_type_groups", **kwargs)


@ddb_site_wrapper
def get_asset_sub_types(asset_type_id: str, url: str = None):
    """Returns all sub types for a given asset type.

    Args:
        asset_type_id (str): Asset type GUID.

    Returns:
        A list of asset sub type dictionaries.
    """
    return requests.get(
        f"{url}asset_types/{asset_type_id}/asset_sub_types",
        headers=headers,
    ).json()["asset_sub_types"]


# Items


def get_item_types(**kwargs):
    """Gets all item types.

    Returns all item types, can be filtered by various keywords:

    Args:
        item_type_id (str): Item type GUID.
        parameter_type_id (str): Parameter type GUID.
        asset_type_id (str): Asset type GUID.

    Returns:
        List of item type dictionaries.
    """
    return get_all(endpoint="item_types", **kwargs)


# Units


def get_units(**kwargs):
    """Gets all units.

    Returns all units, can be filtered to those associated with a given parameter type:

    Args:
        parameter_type_id (str): Parameter type GUID.

    Returns:
        List of unit dictionaries.
    """
    return get_all(endpoint="units", **kwargs)


def get_unit_types(**kwargs):
    """Gets all unit types.

    Returns:
        List of unit type dictionaries.
    """
    return get_all(endpoint="unit_types", **kwargs)


def get_unit_systems(**kwargs):
    """Gets all unit systems.

    Returns:
        List of item type dictionaries.
    """
    return get_all(endpoint="unit_systems", **kwargs)


# Tags


def get_tags(**kwargs):
    """Gets all tags.

    Returns all tags, can be filtered by tag type:

    Args:
        tag_type_id (str): Tag type GUID.

    Returns:
        List of tag type dictionaries.
    """
    return get_all(endpoint="tags", item_limit=9999, **kwargs)


def get_tag_types(**kwargs):
    """Gets all tag types.

    Returns:
        List of tag type dictionaries.
    """
    return get_all(endpoint="tag_types", **kwargs)


def tag_project(project_id, tag_id):
    """Tags a given project.

    Posts a new tag link between a project instance and a tag.

    Args:
        project_id (str): Parameter instance GUID.
        tag_id (str): Tag GUID.
    """
    body = [
        {
            "reference_id": project_id,
            "reference_table": "project",
            "reference_url": "https://my_service.com/api/referenced_elements/",
            "tag_id": tag_id,
        }
    ]
    return post_body(endpoint="tags/links", body=body)


def tag_parameter(parameter_id, tag_id):
    """Tags a given parameter.

    Posts a new tag link between a parameter instance and a tag.

    Args:
        parameter_id (str): Parameter instance GUID.
        tag_id (str): Tag GUID.
    """
    body = [
        {
            "reference_id": parameter_id,
            "reference_table": "parameter",
            "reference_url": "https://my_service.com/api/referenced_elements/",
            "tag_id": tag_id,
        }
    ]
    return post_body(endpoint="tags/links", body=body)


# Classes


class DDB:
    @ddb_site_wrapper
    def get(self, endpoint: str = None, url: str = None, **kwargs):
        """Gets self if ID is given."""
        if not endpoint:
            endpoint = self.endpoint
        payload = generate_payload(**kwargs)
        res = requests.get(f"{url}{endpoint}", params=payload, headers=headers).json()
        # print(res)
        res = res[endpoint][0]
        for key in res:
            setattr(self, key, res[key])
        return res


class Source(DDB):
    """DDB Source object.

    Can be used to post a new source or to get a source by source instance ID.
    """

    def __init__(self, id: str = None):
        """Inits Source class with all source attributes if an id is provided."""
        self.endpoint = "sources"
        if id:
            self.id = id
            self.get(source_id=id)

    def post(
        self,
        project_id: str,
        source_type_id: str,
        source_title: str,
        source_reference: str,
        source_url: str = None,
        source_day: str = None,
        source_month: str = None,
        source_year: str = None,
    ):
        """Posts the source.

        Posts the given source to the given project.
        Source url and reference date is optional.
        Assigns the source attributes and id to self.

        Args:
            project_id: Project GUID.
            source_type_id: Source type GUID.
            source_title: Source title.
            source_reference: Source reference.
            source_url: Source reference url.
            source_day: Source publication day.
            source_month: Source publication month.
            source_year: Source publication year.
        """

        id = add_new_source(
            project_id=project_id,
            source_type_id=source_type_id,
            source_title=source_title,
            source_reference=source_reference,
            source_url=source_url,
            source_day=source_day,
            source_month=source_month,
            source_year=source_year,
        )[0]

        self.get(source_id=id)


class Parameter(DDB):
    """DDB Parameter object.

    Can be used to post a new parameter revision or to tag a parameter.
    """

    def __init__(self, id: str = None):
        """Inits Parameter class with id provided."""
        self.endpoint = "parameters"
        if id:
            self.id = id

    def post_revision(self, value, source_id):
        """Posts a new revision to self.

        Posts a new revision with the provided value and source id.
        self.if must be assigned first.

        Args:
            value (str): Value of the new revision.
            source_id (str): Source instance GUID.
        """
        update_parameters(
            parameter_id=self.id, value=value, unit_id=self.unit_id, source_id=source_id
        )

    def tag(self, tag_id):
        """Tags self.

        Posts a link between the given tag and self.

        Args:
            tag_id (str): Tag GUID."""
        tag_parameter(parameter_id=self.id, tag_id=tag_id)


class Asset(DDB):
    """DDB Asset object.

    Can be used to post a new asset, get an asset by asset instance ID, post or get child assets, or post or get parameters.
    """

    def __init__(self, id: str = None):
        """Inits Asset class with all asset attributes if an id is provided."""
        self.endpoint = "assets"
        if id:
            self.id = id
            self.get(asset_id=id)

    def get_parameters(self):
        """Get all parameters on this asset.

        Assigns a list of parameter dictionaries to the parameters attribute.
        self.id must be assigned first."""
        self.parameters = get_parameters(asset_id=self.id)

    def post(self, asset_type_id, project_id, asset_name, parent_id):
        """Posts a new asset of given type and name to given parent asset.

        If the asset doesn't exist, adds an asset of the given name and type below the parent_id given.
        Assigns self the attributes of the posted asset.

        Args:
            asset_type_id (str): Asset type GUID.
            project_id (str): Project instance GUID.
            asset_name (str): New asset instance name.
            parent_id (str): Parent asset instance GUID."""

        id = add_new_asset(
            asset_type_id=asset_type_id,
            project_id=project_id,
            asset_name=asset_name,
            parent_id=parent_id,
        )
        self.get(asset_id=id)

    def post_parameters(self, parameter_type_id, value, unit_id, source_id):
        """Posts new parameter(s) or updates existing parameters with new revisions.

        Posts a given parameter to self, with the provided value, unit, and source.
        If it already exists and the value is different, creates a new revision instead.
        A list of types, values, units, and source ids can be provided to upload multiple values at once.
        Assigns parameters to self.parameters.

        Args:
            parameter_type_id (str): Parameter type GUID
            value (str): Parameter value
            unit_id (str): Unit GUID
            source_id (str): Source instance GUID
        """

        add_update_parameter(
            parameter_type_id=parameter_type_id,
            project_id=self.project_id,
            asset_id=self.id,
            value=value,
            unit_id=unit_id,
            source_id=source_id,
        )
        self.get_parameters()

    def get_assets(self):
        """Gets all child assets.

        Gets all asset that have this asset id as their parent id.
        self.id must be assigned first.
        Assigns a list of Asset objects to self.assets."""
        self.assets = [Asset(id=x["id"]) for x in get_assets(parent_id=self.id)]

    def post_assets(self, asset_type_id, asset_name):
        """Posts a new asset of given type and name below self.

        If the asset doesn't exist, adds an asset of the given name and type with self as the parent asset.
        Refreshes self.assets.

        Args:
            asset_type_id (str): Asset type GUID.
            asset_name (str): New asset instance name.

        Returns:
            Asset oject of posted asset."""
        asset_id = add_new_asset(
            asset_type_id=asset_type_id,
            project_id=self.project_id,
            asset_name=asset_name,
            parent_id=self.id,
        )
        self.get_assets()
        return Asset(id=asset_id)


class Project(DDB):
    """DDB Project object.

    Can be used to post a new project, get a project by project number, post or get child assets, post or get parameters, or to tag a project."""

    def __init__(self, job_number: str = None):
        """Inits Project class with job_number attribute and attempts to post the project."""
        self.endpoint = "projects"
        if job_number:
            self.job_number = job_number
            self.post()

    def get_assets(self):
        """Gets all child assets.

        Gets all asset that have this asset id as their parent id.
        self.id must be assigned first.
        Assigns a list of Asset objects to self.assets."""

        self.assets = [
            Asset(id=x["id"]) for x in get_assets(project_id=self.project_id)
        ]

    def post(self):
        """Posts self."""
        add_new_project(job_number=self.job_number)

        self.get(number=self.job_number)

    def post_assets(self, asset_type_id, asset_name):
        """Posts a new asset of given type and name below self.

        If the asset doesn't exist, adds an asset of the given name and type with self as the parent asset.

        Args:
            asset_type_id (str): Asset type GUID.
            asset_name (str): New asset instance name.

        Returns:
            Asset oject of posted asset."""

        asset_id = add_new_asset(
            asset_type_id=asset_type_id,
            project_id=self.project_id,
            asset_name=asset_name,
        )

        # self.get_assets()
        return Asset(id=asset_id)

    def get_parameters(self):
        """Get all parameters on this asset.

        Assigns a list of parameter dictionaries to the parameters attribute.
        self.id must be assigned first."""

        self.parameters = [
            Parameter(id=x["id"])
            for x in get_parameters(project_id=self.project_id, project_parameter=True)
        ]

    def post_parameters(self, parameter_type_id, value, unit_id, source_id):
        """Posts new parameter(s) or updates existing parameters with new revisions.

        Posts a given parameter to self, with the provided value, unit, and source.
        If it already exists and the value is different, creates a new revision instead.
        A list of types, values, units, and source ids can be provided to upload multiple values at once.
        Assigns parameters to self.parameters.

        Args:
            parameter_type_id (str): Parameter type GUID
            value (str): Parameter value
            unit_id (str): Unit GUID
            source_id (str): Source instance GUID
        """
        add_update_parameter(
            parameter_type_id=parameter_type_id,
            project_id=self.project_id,
            asset_id="",
            value=value,
            unit_id=unit_id,
            source_id=source_id,
        )
        self.get_parameters()

    def tag(self, tag_id):
        """Tags self.

        Posts a link between the given tag and self.

        Args:
            tag_id (str): Tag GUID."""
        tag_project(project_id=self.project_id, tag_id=tag_id)
