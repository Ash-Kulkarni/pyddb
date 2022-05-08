"""Library for getting and posting values to the Digital Design Brief database.

Functions and classes to create and retreive projects, assets, parameters, and values.
"""


# # Sources


# def add_new_source(
#     project_id: str,
#     source_type_id: str or list,
#     source_title: str or list,
#     source_reference: str or list,
#     source_url: str = None,
#     source_day: str = None,
#     source_month: str = None,
#     source_year: str = None,
# ):
#     """Posts new source(s) to a project.

#     Posts new source(s) to the given project GUID.  Source type, title, and reference are mandatory.
#     Source url and reference day, month, and year are optional.
#     Lists of source information can be provided to post multiple sources.

#     Args:
#         project_id: Project GUID.
#         source_type_id: Source type GUID.
#         source_title: Source title.
#         source_reference: Source reference.
#         source_url: Source reference url.
#         source_day: Source publication day.
#         source_month: Source publication month.
#         source_year: Source publication year.

#     Returns:
#         A list containing the source instance ID(s) in the order given.
#     """
#     (
#         source_type_id,
#         source_title,
#         source_reference,
#         source_url,
#         source_day,
#         source_month,
#         source_year,
#     ) = convert_to_lists(
#         source_type_id,
#         source_title,
#         source_reference,
#         source_url,
#         source_day,
#         source_month,
#         source_year,
#     )
#     source_url = [None if x == "" else x for x in source_url]
#     source_ids = []
#     failed_sources = []

#     existing_sources = get_sources(
#         reference_id=project_id, page_limit=9999
#     )  # get existing sources
#     # print(existing_sources)
#     for i, _ in enumerate(
#         source_type_id
#     ):  # for each new source, check if it already exists
#         existing_source_ids = [
#             existing_source["id"]
#             for existing_source in existing_sources
#             if existing_source["title"] == source_title[i]
#             and existing_source["reference"] == source_reference[i]
#             and existing_source["source_type"]["id"] == source_type_id[i]
#             and existing_source["url"] == source_url[i]
#         ]

#         if existing_source_ids != []:
#             source_ids.append(existing_source_ids[0])  # if it exists, find its id
#         else:  # otherwise, post it and retreive its id

#             source = {
#                 "source_type_id": source_type_id[i],
#                 "title": source_title[i],
#                 "reference": source_reference[i],
#                 "reference_id": project_id,
#                 "reference_table": "projects",
#                 "reference_url": "https://ddb.arup.com/project",
#             }

#             if source_url[i]:
#                 source["url"] = source_url[i]
#             if source_day[i]:
#                 source["date_day"] = source_day[i]
#             if source_month[i]:
#                 source["date_month"] = source_month[i]
#             if source_year[i]:
#                 source["date_year"] = source_year[i]

#             res = post_request(endpoint="sources/", body=source)

#             if "details" in res:
#                 print(f"Error: {res['details']}")
#                 failed_sources.append(source)
#             new_source_id = res["source"]["id"]
#             # print("Source created successfully.")
#             source_ids.append(new_source_id)
#     # print(f"{len(source_ids)} source(s) located.")
#     if failed_sources:
#         print(
#             f"The following ({len(failed_sources)}) sources failed: {pp(failed_sources)}"
#         )
#     return source_ids


# # Parameters


# def add_new_parameters(
#     parameter_type_id: str or list,
#     project_id: str,
#     asset_id: str = None,
#     value: str or list = None,
#     unit_id: str or list = None,
#     source_id: str or list = None,
# ):
#     """Posts new parameter, does not update/create new revision.
#     Use add_update_parameter() instead.
#     """

#     parameter_type_id, value, unit_id, source_id = convert_to_lists(
#         parameter_type_id, value, unit_id, source_id
#     )

#     l = range(len(parameter_type_id))

#     # batch size for batched parameter upload is 12

#     batch_size = 1
#     chunks = [l[i : i + batch_size] for i in range(0, len(l), batch_size)]

#     if asset_id:
#         p_ids = []
#         for chunk in chunks:

#             new_parameters = {"parameters": []}

#             for i in chunk:

#                 i -= 1
#                 new_parameters["parameters"].append(
#                     {
#                         "parameter_type_id": parameter_type_id[i],
#                         "project_id": project_id,
#                         "parent_ids": asset_id,
#                         "revision": {
#                             "source_id": source_id[i],
#                             "comment": "Python Upload",
#                             "location_in_source": "Python",
#                             "values": [{"value": value[i], "unit_id": unit_id[i]}],
#                         },
#                     }
#                 )
#             a = post_request(endpoint="parameters/", body=new_parameters)

#             if "details" in a:
#                 print(f"{a['details']}.")
#                 if "already exists" in a["details"]:
#                     print("To update parameters, use a different function.")
#                     return
#                 else:
#                     return f"Error: {a['details']}."
#             print(f"Parameter posted successfully.")
#             p_ids += [x["id"] for x in a["parameters"]]
#             return

#     else:
#         p_ids = []
#         for chunk in chunks:
#             p_ids = []
#             new_parameters = {"parameters": []}

#             for i in chunk:

#                 i -= 1

#                 new_parameters["parameters"].append(
#                     {
#                         "parameter_type_id": parameter_type_id[i],
#                         "project_id": project_id,
#                         "revision": {
#                             "source_id": source_id[i],
#                             "comment": "Python Upload",
#                             "location_in_source": "Python",
#                             "values": [{"value": value[i], "unit_id": unit_id[i]}],
#                         },
#                     }
#                 )

#             # a = requests.post(f"{url}parameters/", json=new_parameters, headers=headers).json()
#             a = post_request(endpoint="parameters", body=new_parameters)

#             if "details" in a:
#                 print(f"Error: {a['details']}.")
#                 if "already exists" in a["details"]:
#                     return "To update parameters use a different function."
#             if "details" in a:
#                 return f"Error: {a['details']}."

#             p_ids += [x["id"] for x in a["parameters"]]

#         if p_ids:
#             print(f"Parameter posted successfully.")
#             return p_ids
#         else:
#             print("No new parameters posted.")
#             return


# def update_parameters(
#     parameter_id: str or list,
#     value: str or list,
#     unit_id: str or list,
#     source_id: str or list,
# ):
#     """Updates a given parameter.
#     Use add_update_parameter() instead.
#     """

#     parameter_id, value, unit_id, source_id = convert_to_lists(
#         parameter_id, value, unit_id, source_id
#     )

#     if parameter_id == []:  ## hack
#         return
#     # creates a dictionary of the existing value and source id for each parameter_id entered
#     existing_parameters_dict = {
#         id: {"value": value, "source": source}
#         for (id, value, source) in [
#             (
#                 x["id"],
#                 x["revision"]["values"][0]["value"],
#                 x["revision"]["source"]["id"],
#             )
#             for x in get_parameters(parameter_id=parameter_id)
#         ]
#     }
#     for i, parameter_id in enumerate(parameter_id):

#         # check if value or source have changed
#         if (
#             existing_parameters_dict[parameter_id]["value"] == value[i]
#             and existing_parameters_dict[parameter_id]["source"] == source_id[i]
#         ):
#             continue

#         updated_parameter = {
#             "source_id": source_id[i],
#             "values": [{"value": value[i], "unit_id": unit_id[i]}],
#         }

#         # response = requests.post(f"{url}parameters/" + parameter_id + "/revision", json=updated_parameter, headers=headers).json()
#         response = post_request(
#             endpoint=f"parameters/{parameter_id}/revision", body=updated_parameter
#         )
#         if "details" in response:
#             print(f"Error: {response['details']}.")
#             return
#     return parameter_id


# def check_parameter_exists(
#     parameter_type_id: list, asset_id: str = None, project_id: str = None
# ):
#     """Checks if parameter type exists on an asset or at project level.

#     Checks if a parameter type instance exists on a specified asset instance.
#     Checks project level on the given project_id if no asset_id is given.

#     Args:
#         **asset_id (str): Asset instance GUID
#         **asset_type (str): Asset type GUID
#         **parameter_id (str): Parameter instance GUID
#         **parameter_type_id (str): Parameter type GUID
#         **project_id (str): Project instance GUID
#         **category_id (str): Tag instance GUID
#         **report_id (str): Tag instance GUID
#         **discipline_id (str): Tag instance GUID
#         **source_id (str): Source instance GUID
#         **source_type_id (str): Source type GUID
#         **qa_status (str): Must be one of: "unanswered", "answered", "checked", "approved", or "rejected"
#         **unit_id (str): Unit GUID

#     Returns:
#         True or False
#     """
#     if asset_id:
#         parameters = get_parameters(asset_id=asset_id)
#     else:
#         parameters = get_parameters(project_id=project_id, project_parameter=True)

#     parameter_types = [x["parameter_type"]["id"] for x in parameters]

#     return [True if x in parameter_types else False for x in parameter_type_id]


# def add_update_parameter(
#     parameter_type_id: str or list,
#     project_id: str,
#     asset_id: str = None,
#     value: str or list = None,
#     unit_id: list = None,
#     source_id: str or list = None,
# ):
#     """Posts a new parameter or a new entry for the existing one.

#     Posts a given parameter to an asset_id, with the provided value, unit, and source.
#     If it already exists and the value is different, creates a new revision instead.
#     A list of types, values, units, and source ids can be provided to upload multiple values to a single asset.

#     Args:
#         parameter_type_id (str): Parameter type GUID
#         project_id (str): Project instance GUID
#         asset_id: str = Asset isntance GUID
#         value (str): Parameter value
#         unit_id (str): Unit GUID
#         source_id (str): Source instance GUID
#     """

#     # check if exist
#     parameter_type_id, value, unit_id, source_id = convert_to_lists(
#         parameter_type_id, value, unit_id, source_id
#     )
#     if asset_id:
#         parameter_exists_list = check_parameter_exists(
#             asset_id=asset_id, parameter_type_id=parameter_type_id
#         )
#     else:
#         parameter_exists_list = check_parameter_exists(
#             project_id=project_id, parameter_type_id=parameter_type_id
#         )

#     new = {
#         "parameter_type_id": [],
#         "value": [],
#         "unit_id": [],
#         "source_id": [],
#     }

#     update = {
#         "parameter_id": [],
#         "value": [],
#         "unit_id": [],
#         "source_id": [],
#     }

#     for i, exist in enumerate(parameter_exists_list):
#         if exist == False:

#             new["parameter_type_id"].append(parameter_type_id[i])
#             new["value"].append(value[i])
#             new["unit_id"].append(unit_id[i])
#             new["source_id"].append(source_id[i])

#         else:
#             update["value"].append(value[i])
#             update["unit_id"].append(unit_id[i])
#             update["source_id"].append(source_id[i])
#             if asset_id:
#                 update["parameter_id"].append(
#                     get_parameters(
#                         asset_id=asset_id, parameter_type_id=parameter_type_id[i]
#                     )[0]["id"]
#                 )
#             else:
#                 update["parameter_id"].append(
#                     get_parameters(
#                         project_id=project_id,
#                         parameter_type_id=parameter_type_id[i],
#                         project_parameter=True,
#                     )[0]["id"]
#                 )

#     new_ids = add_new_parameters(
#         new["parameter_type_id"],
#         project_id,
#         asset_id,
#         new["value"],
#         new["unit_id"],
#         new["source_id"],
#     )

#     updated_ids = update_parameters(
#         update["parameter_id"],
#         update["value"],
#         update["unit_id"],
#         update["source_id"],
#     )

#     parameter_ids = []
#     if new_ids:
#         parameter_ids += list(new_ids)
#     if updated_ids:
#         parameter_ids += list(updated_ids)
#     return  # parameter_ids


# # Parameter Revisions


# @response_serializer()
# @ddb_site_wrapper
# def get_request_revisions(parameter_id: str, url: str = None) -> List[Revision]:
#     """Returns a list of revision objects for a given parameter_id.

#     Args:
#         parameter_id (str): Parameter instance GUID

#     Returns:
#         Dictionary of parameter revisions.
#     """
#     return requests.get(
#         f"{url}parameters/{parameter_id}/revision", headers=headers
#     ).json()


# @ddb_site_wrapper
# def patch_revision_status(
#     parameter_id: str, new_status: str = None, comment: str = None, url: str = None
# ):
#     """Updates a value's QA status.

#     Updates status from answered to checked or checked to approved.
#     The status can be reduced to any level below.
#     Values can be rejected with a comment at any stage.

#     Args:
#         parameter_id (str): Parameter instance GUID
#         new_status (str): New QA status, must be one of: "unanswered", "answered", "checked", "approved", or "rejected"
#         comment (str): A comment about why the value was rejected.

#     Returns:
#         Revised parameter JSON.
#     """
#     s = ["answered", "checked", "approved", "rejected"]
#     body = {}

#     if new_status and new_status not in s:
#         print(f"Revision status must be one of {s}")
#     else:
#         body["status"] = new_status
#         if comment:
#             body["comment"] = comment

#     return requests.patch(
#         f"{url}parameters/{parameter_id}/revision", json=body, headers=headers
#     ).json()


# # Projects


# def add_new_project(job_number: str):
#     """Posts a new project to DDB.

#     Takes an 8 digit project number and posts the project to DDB.
#     The project must exist in the Arup intranet.

#     Args:
#         job_number (str): 8 digit project number.

#     Returns:
#         The project instance GUID.
#     """
#     body = {"number": str(job_number)}

#     res = post_request(endpoint="projects", body=body)

#     if "projects" in res:
#         print("Project created successfully.  Project ID retreived.")
#         project_id = res["projects"][0]["project_id"]
#         return project_id

#     if "msg" in res:
#         if res["msg"] == "Conflict":
#             print("Existing Project Found.")
#             return get_project_id(job_number)

#     if "details" in res:
#         print(f"Error: {res['details']}")
#         return

#     else:
#         print("Unknown error.")
#         return


# def get_project_id(job_number):
#     """Gets a project instance GUID.

#     Takes an 8 digit project number and retreives the project instance GUID.
#     The project must exist in the Arup intranet.

#     Args:
#         job_number (str): 8 digit project number.

#     Returns:
#         The project instance GUID.
#     """
#     try:
#         return self.get_request(endpoint="projects", number=job_number)[0]["project_id"]
#     except IndexError:
#         print("Project not found.")
#         return


# # Assets


# def add_new_asset(
#     asset_type_id: str, project_id: str, asset_name: str, parent_id: str = None
# ):
#     """Adds a new asset to a project.

#     Checks if the asset already exists, if it does, returns asset instance GUID.
#     Otherwise, adds an asset of the given name and type below the parent_id given.

#     Args:
#         asset_type_id (str): Asset type GUID.
#         project_id (str): Project instance GUID.
#         asset_name (str): New asset instance name.
#         parent_id (str): Parent asset instance GUID.

#     Returns:
#         Asset instance GUID
#     """
#     asset_id = check_asset_exists(project_id, asset_type_id, parent_id, asset_name)
#     if asset_id == False:
#         asset = {
#             "assets": [
#                 {
#                     "asset_type_id": asset_type_id,
#                     "project_id": project_id,
#                     "name": asset_name,
#                 }
#             ]
#         }

#         if parent_id:
#             asset["assets"][0]["parent_id"] = parent_id

#         # a = requests.post(f"{url}assets", json=asset, headers=headers).json()
#         a = post_request(endpoint="assets", body=asset)

#         print(f"Asset: {asset_name} created successfully.")
#         return a["assets"][0]["id"]
#     else:
#         print(f"Asset: {asset_name} already exists.")
#         return asset_id


# @ddb_site_wrapper
# def check_asset_exists(
#     project_id, asset_type_id, parent_id, asset_name, url: str = None
# ):
#     """Checks if an asset exists.

#     Checks if an asset of the given name and type exist under the given parent asset.
#     If the parent_id is None, searches the whole project, used for level 0 assets.

#     Args:
#         project_id (str): Project instance GUID.
#         asset_type_id (str): Asset type GUID of the asset you are checking for.
#         parent_id (str): Parent asset instance GUID.
#         asset_name (str): Name of the asset you are checking for.

#     Returns:
#         Asset instance GUID or False.
#     """
#     parent_query = f"&parent_id={parent_id}" if parent_id != None else ""

#     a = requests.get(
#         f"{url}assets?asset_type_id={asset_type_id}{parent_query}&project_id={project_id}&show_deleted_assets=false",
#         headers=headers,
#     ).json()

#     if "details" in a:
#         return f"Error: {a['details']}"
#     if "msg" in a:
#         return "Error: Check asset_type_id."
#     b = [x["id"] for x in a["assets"] if x["name"] == asset_name]

#     if b == []:
#         return False
#     else:
#         return b[0]


# # returns the ordered hierarchies of given asset's parents
# @ddb_site_wrapper
# def get_hierarchy(asset_id: str, url: str = None):
#     """Returns the ordered hierarchies of a given assets parents.

#     Args:
#         asset_id (str): Asset instance GUID.

#     Returns:
#         List of asset dictionaries of parent asset instances:

#         [{
#             "id": "933c36d0-8158-4d28-8c2d-319a33b92312",
#             "name": "Wellington Place"
#         },
#         {
#             "id": "62f3f99c-1bf5-4fd4-97e9-ef9f3af40879",
#             "name": "4 Wellington Place"
#         },
#         {
#             "id": "87a10e7a-a0b7-4fd1-b4b7-b2f5ffc128a0",
#             "name": "Hot Water"
#         }]
#     """
#     return requests.get(f"{url}assets/{asset_id}/hierarchy", headers=headers).json()[
#         "hierarchies"
#     ][0]


# # Asset Types


# @response_serializer()
# @ddb_site_wrapper
# def get_asset_sub_types(asset_type_id: str, url: str = None) -> List[AssetSubType]:
#     """Returns a list of all sub type objects for a given asset type.

#     Args:
#         asset_type_id (str): Asset type GUID.

#     Returns:
#         A list of asset sub type dictionaries.
#     """
#     return requests.get(
#         f"{url}asset_types/{asset_type_id}/asset_sub_types",
#         headers=headers,
#     ).json()["asset_sub_types"]


# # Items


# def tag_project(project_id, tag_id):
#     """Tags a given project.

#     Posts a new tag link between a project instance and a tag.

#     Args:
#         project_id (str): Parameter instance GUID.
#         tag_id (str): Tag GUID.
#     """
#     body = [
#         {
#             "reference_id": project_id,
#             "reference_table": "project",
#             "reference_url": "https://my_service.com/api/referenced_elements/",
#             "tag_id": tag_id,
#         }
#     ]
#     return post_request(endpoint="tags/links", body=body)


# def tag_parameter(parameter_id, tag_id):
#     """Tags a given parameter.

#     Posts a new tag link between a parameter instance and a tag.

#     Args:
#         parameter_id (str): Parameter instance GUID.
#         tag_id (str): Tag GUID.
#     """
#     body = [
#         {
#             "reference_id": parameter_id,
#             "reference_table": "parameter",
#             "reference_url": "https://my_service.com/api/referenced_elements/",
#             "tag_id": tag_id,
#         }
#     ]
#     return post_request(endpoint="tags/links", body=body)


# # Classes
