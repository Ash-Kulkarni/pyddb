from pandas.core.frame import DataFrame
import ddb_get_post as pyddb
import pandas as pd
import itertools
import uuid
import datetime

# all assets, parameters, values, sources on project - probably should add parent parent asset id +/ name
def get_project_df(project_id):
    df = pd.DataFrame.from_records(
        [pyddb.flatten_data(x) for x in pyddb.get_parameters(project_id=project_id)]
    )

    a = [
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
    ]

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

    df_simple = df[a].copy()
    df_simple.rename(columns=b, inplace=True)

    return df_simple


def get_project_assets_df(project_id):
    df = pd.DataFrame.from_records(
        [pyddb.flatten_data(x) for x in pyddb.get_assets(project_id=project_id)]
    )
    a = ["asset_type_name", "name", "id", "parent"]

    b = {
        "asset_type_name": "Asset Type",
        "name": "Asset",
        "id": "Asset ID",
        "parent": "Parent Asset ID",
    }

    df_simple = df[a].copy()
    df_simple.rename(columns=b, inplace=True)

    return df_simple


def get_asset_parameters_df(asset_id):
    df = pd.DataFrame.from_records(
        [pyddb.flatten_data(x) for x in pyddb.get_parameters(asset_id=asset_id)]
    )

    a = [
        "parameter_type_name",
        "revision_values_0_value",
        "revision_values_0_unit_name",
        "revision_source_source_type_name",
        "revision_source_title",
        "revision_source_reference",
    ]

    b = {
        "parameter_type_name": "Parameter Type",
        "revision_values_0_value": "Value",
        "revision_values_0_unit_name": "Unit",
        "revision_source_source_type_name": "Source Type",
        "revision_source_title": "Source Title",
        "revision_source_reference": "Source Reference",
    }

    df_simple = df[a].copy()
    df_simple.rename(columns=b, inplace=True)

    return df_simple


def get_project_parameters_df(project_id):
    df = pd.DataFrame.from_records(
        [
            pyddb.flatten_data(x)
            for x in pyddb.get_parameters(project_id=project_id, project_parameter=True)
        ]
    )
    a = [
        "parameter_type_name",
        "revision_values_0_value",
        "revision_values_0_unit_name",
        "revision_source_source_type_name",
        "revision_source_title",
        "revision_source_reference",
    ]

    b = {
        "parameter_type_name": "Parameter Type",
        "revision_values_0_value": "Value",
        "revision_values_0_unit_name": "Unit",
        "revision_source_source_type_name": "Source Type",
        "revision_source_title": "Source Title",
        "revision_source_reference": "Source Reference",
    }

    df_simple = df[a].copy()
    df_simple.rename(columns=b, inplace=True)

    return df_simple


def get_project_sources_df(project_id):
    df = pd.DataFrame.from_records(
        [pyddb.flatten_data(x) for x in pyddb.get_sources(reference_id=project_id)]
    )
    a = ["title", "reference", "source_type_name", "id"]

    b = {
        "title": "Source Title",
        "reference": "Source Reference",
        "source_type_name": "Source Type",
        "id": "Source ID",
    }

    df_simple = df[a].copy()
    df_simple.rename(columns=b, inplace=True)

    return df_simple


def download_df(df: DataFrame, name: str):

    df.to_csv(f"{name}.csv", index=False)
    print(f"Dataframe saved as {name}.csv")
    return


### Bulk Upload Tool


def generate_guid_dicts():
    source_types = {
        name: id
        for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_source_types()]
    }

    tag_types = {
        name: id for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_tags()]
    }
    tag_types["no tag"] = ""

    units = {
        name: id for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_units()]
    }
    units[0] = None

    parameter_types = {
        name: id
        for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_parameter_types()]
    }

    asset_types = get_asset_type_dict()
    return source_types, tag_types, units, parameter_types, asset_types


def get_asset_type_dict():
    asset_types = {
        "site": "a98d79a1-4f4a-42e5-ac28-0773387b3dfe",
        "building": "dbeac84d-9235-47fb-ae08-c8d47e00f253",
        "space type": "ef25209b-f506-464c-9592-6f057c900e23",
        "space instance": "21ba5fbb-f079-4c37-a3b9-f36e21e5b3ac",
        "system (buildings)": "577cfd8d-8da0-4d78-b4a4-c81ab728d4bf",
        "sub system": "e4b51a06-4f87-4108-9fac-fe44182621fb",
        "frame (buildings)": "e93e918e-5f06-4a6d-9ddf-fd3978c0a2af",
        "sub frame": "d5e9c6dd-e0b8-4a54-8bdb-5806dcc7cac8",
        "building envelope": "90b96895-bd5a-4a2f-9bfc-ae90076ac461",
        "material (buildings)": "807b2cd2-5a7f-4dc7-9f53-1aab41cc7d06",
        "network link": "fb7e2a70-3f23-44c0-a95e-79fd53f611f5",
        "network asset": "eea5f226-c1d4-47d9-9c14-2994f454fcfe",
        "system (infrastructure)": "612116fa-2b32-4264-9122-e7a9a865b9a9",
        "component": "37b7c025-68c1-4407-8285-8214e5bc6384",
        "element type (buildings)": "6ef368d8-ef5e-4d16-91e1-2e7159cdfbd9",
        "element sub-type": "b0485717-c05b-4548-9e70-b88a3847f409",
        "element instance": "385ff8a3-e952-458f-aeb6-b935b2978daa",
        "frame (infrastructure)": "2238170e-9334-47b4-8e8c-87f2422b12a7",
        "element type (infrastructure)": "2353e503-097c-4099-b1f0-b88f65ef25bd",
        "area (buildings)": "f61f7053-b28e-457a-b719-c04d7e1536a3",
        "masterplanning site": "cc71ec13-c3d1-4ac2-bfbb-49b8da3a0dd9",
        "plot": "5cd80985-6d65-41b1-9e6e-344cae9f4610",
        "equipment type": "9f6df491-99a3-4977-b90c-ee4713d68960",
        "equipment sub type": "8222f1f9-9419-4b9b-aa6f-cb724e91084d",
        "element sub type": "9f930069-0610-4512-8d09-3c2420fc221a",
        "alignment": "735600cc-97db-45a5-b152-bc3a4095a23d",
        "sub component": "45e448af-50b3-46c9-873b-76657a349ad1",
        "facade sub system": "02b4ddb3-9564-46f4-bd7e-40eea94070c5",
        "facade element": "cffa3ee4-b54d-45e8-840d-56721cf2c28f",
        "facade sub element": "893a1ea1-bfba-4f84-bbc5-2a35a296fa04",
        "product type": "49202b68-1ff9-489b-a8ff-9e7d890f1bf4",
        "area": "c6e532b9-1fa6-4ec0-ade3-3a6bd9c7a0ea",
        "ground model": "f064c07d-e315-47a1-a840-9a6de60e1a87",
        "layer": "5383f5f9-a0d7-40c5-817f-f60c7f0e8200",
        "case": "b237bb02-ae2d-489b-9d8f-02ac5e458527",
        "assembly": "88992a66-7047-4c8e-bfa5-06058363a989",
        "2nd level sub component": "16954e25-c6d0-41e1-b15e-4f6322f379ad",
        "3rd level sub component": "f1ab5778-9dc9-4f0f-b047-8a801d9f7424",
        "tunnel vent": "66a544a8-efa4-42ed-bdb1-fae3fdc78264",
        "vehicles": "962ad0d3-b432-420d-92b5-bd72f57649fe",
        "railway": "f623b5a6-af2d-4e42-9604-daae942ab5bc",
        "track type": "a1a3aac2-5797-4f80-9ea0-f437b62b688d",
        "wire run": "d03d830e-6560-4a1b-b4d6-8b8999cb0962",
        "overhead line engineering": "0b611f73-3121-41b7-bb09-7dd6059db2a1",
        "track subtype": "2e888965-f198-42a8-8210-e5f6b9b51571",
        "bed formation": "4a5734c8-3e34-40b3-ae74-303faee78e0b",
        "alignment (track)": "b2638d78-fdb4-414f-892f-ee49f0ca2b4e",
        "span": "d0f6bf07-2527-4607-b567-21207de5c221",
        "in span equipment": "3e60c861-a46f-49d0-8b35-506c234cabbb",
        "bridge": "b5219a7f-3d62-4e32-8a3a-11458a6ab804",
        "bridge components": "3b6cbc7a-cda0-4062-b635-d6baf83797f2",
        "deck / support / non-structural elements": "6c607416-4f2c-4437-88bc-11687c383402",
        "primary deck element": "b1c92fe6-8ce9-4a13-b748-636f2ed9d1a3",
        "transverse beam": "a0178851-8e07-4136-b203-e4a94eb09a60",
        "secondary deck element": "243bf1dd-5f5a-405b-94b5-da41e7c0cd5b",
        "other deck element": "9487d395-77dc-4002-98e2-31d86d4875d9",
        "cable system": "6090ae05-7e58-46b2-bf0e-d4412fe3963d",
        "load-bearing substructure": "d5b8c5ac-20ee-495f-b4f4-ee6f2139673f",
        "foundations": "26b32ca3-cbe5-47c7-8190-ccc12e4edb47",
        "durability elements": "875d52fd-d124-42b9-8384-5f38291d69dd",
        "safety elements": "86eb040a-2240-4f5f-be97-a51481f2e837",
        "other bridge elements": "b0186a52-c649-4139-9f63-f0e54548e7d0",
        "ancilliary elements": "f9e50db4-74d0-42b9-8623-933a3a76ae79",
        "mechanical and electrical systems": "02d25162-f42f-4979-bfb4-72b883aada9d",
        "material": "c8057e13-2d29-4841-b64a-b6e1c95d7b5d",
        "Project": None,
    }

    return asset_types


def post_all_assets(df, project_id, asset_types):
    asset_dict = {"Project": None}
    df[["Asset Type"]] = df[["Asset Type"]].fillna(value="")
    df[["Parent Asset Chain"]] = df[["Parent Asset Chain"]].fillna(value="")

    assets = df[["Asset Type", "Asset Name", "Parent Asset Chain"]].values.tolist()
    # assets = [x.split(",./") for x in list(set([x[0]+",./"+x[1]+",./"+x[2] for x in gross_assets]))]

    for asset in assets:
        if asset[1] != "Project":
            this_asset = pyddb.Asset()
            this_asset.post(
                asset_type_id=asset_types[asset[0].lower()],
                project_id=project_id,
                asset_name=asset[1],
                parent_id=asset_dict[asset[2]],
            )

            asset_dict[asset[1] + asset[2]] = this_asset.id
    return asset_dict


def post_all_sources(df, project_id, source_types):
    df[["Source Type", "Source Title", "Source Reference"]] = df[
        ["Source Type", "Source Title", "Source Reference"]
    ].fillna(value="no source")

    gross_sources = df[
        [
            "Source Type",
            "Source Title",
            "Source Reference",
            "Source URL",
            "Day",
            "Month",
            "Year",
        ]
    ].values.tolist()

    mod = "1246633d-9e75-4fcd-ba0e-0513ff24ed37"
    sources = [x.split(mod) for x in list(set([mod.join(x) for x in gross_sources]))]

    source_dict = {}

    for source in sources:
        if source[0] != "no source":
            source_dict[source[0] + source[1] + source[2]] = pyddb.add_new_source(
                project_id=project_id,
                source_type_id=source_types[source[0]],
                source_title=source[1],
                source_reference=source[2],
                source_url=source[3],
                source_day=source[4],
                source_month=source[5],
                source_year=source[6],
            )[0]
    return source_dict


def post_all_parameters(
    df, project_id, asset_dict, source_dict, parameter_types, units
):
    parameters = df[
        [
            "Parameter Type",
            "Parent Asset Chain",
            "Asset Name",
            "Value",
            "Unit",
            "Source Type",
            "Source Title",
            "Source Reference",
        ]
    ].values.tolist()
    for parameter in parameters:
        if parameter[3] != "no value":
            if (
                parameter[5] != "no source"
                and parameter[6] != "no source"
                and parameter[7] != "no source"
            ):
                pn = parameter[0].replace("\xa0", " ")
                pyddb.add_update_parameter(
                    parameter_type_id=parameter_types[pn],
                    project_id=project_id,
                    asset_id=asset_dict[parameter[2] + parameter[1]],
                    value=parameter[3],
                    unit_id=units[parameter[4]],
                    source_id=source_dict[parameter[5] + parameter[6] + parameter[7]],
                )


def generate_asset_lists(df, project_id, asset_types_map):
    """Generates lists of asset types, project ids, asset names, asset ids, and parent names.

    Takes the dataframe from the bulk upload template and a project_id.
    Reads the asset-related columns, removes any blanks, project rows, and duplicates.
    Creates a dictionary of all assets and generates GUIDs for them.
    """
    asset_ids = []
    asset_dict = {"Project": None}
    df[["Asset Type"]] = df[["Asset Type"]].fillna(value="")
    df[["Parent Asset Chain"]] = df[["Parent Asset Chain"]].fillna(value="")

    # Remove duplicates
    a_list = df[["Asset Type", "Asset Name", "Parent Asset Chain"]].values.tolist()
    a_list.sort()
    a_list = list(a_list for a_list, _ in itertools.groupby(a_list))
    a_list.pop(0)  # removes project - check this

    # create list of asset types, names, ids, parents
    asset_type_ids, asset_names, asset_ids = list(map(list, zip(*a_list)))
    asset_type_ids = [asset_types_map[a] for a in asset_type_ids]
    for a in a_list:
        asset_dict[a[1] + a[2]] = str(uuid.uuid4())
    asset_ids = [asset_dict[a[1] + a[2]] for a in a_list]
    parent_names = [a[2] for a in a_list]
    a_name_dict = {a[1] + a[2]: a[1] for a in a_list}
    a_name_dict["Project"] = ""
    project_ids = [project_id] * len(asset_ids)

    return (
        asset_dict,
        asset_type_ids,
        project_ids,
        asset_names,
        asset_ids,
        parent_names,
        a_name_dict,
    )


def bulk_post_assets(
    asset_dict,
    asset_type_id: str,
    project_ids: str,
    asset_name: str,
    asset_ids: list,
    a_name_dict: dict,
    asset_types_map: dict,
    parent_name: str = None,
):
    """Uploads lists of assets.

    Takes a dictionary of asset names and GUIDs, lists of asset type ids,
    project ids, asset names, asset ids, and parent asset names.

    Checks for existing assets, adds their ids to the dictionary.
    Constructs a body of all new assets and posts them.

    Returns:
        Dictionary of asset names and GUIDS.
    """
    assets = {"assets": []}

    def g(project_id):
        return pyddb.get_assets(project_id=project_id)

    # get all assets on the project and build a dictionary of their names and GUIDS.
    project_assets = g(project_ids[0])
    existing_asset_dict = {
        id: name for (id, name) in [(x["id"], x["name"]) for x in project_assets]
    }

    # list of existing level 0 assets
    e_0 = [
        (existing_asset["name"], existing_asset["asset_type"]["id"])
        for existing_asset in project_assets
    ]
    existing_asset_dict[None] = "Project"
    # list of all existing assets
    e = [
        [
            existing_asset["name"],
            existing_asset["asset_type"]["id"],
            existing_asset_dict[existing_asset["parent"]],
        ]
        for existing_asset in project_assets
    ]

    for i, _ in enumerate(asset_type_id):
        a = [asset_name[i], asset_type_id[i], a_name_dict[parent_name[i]]]

        # checks if asset already exists
        if a in e:

            id = [
                x["id"]
                for x in project_assets
                if x["asset_type"]["id"] == a[1]
                and x["name"] == a[0]
                and existing_asset_dict[x["parent"]] == a_name_dict[parent_name[i]]
            ]

            if id and type(id) == list:
                id = id[0]

            # adds id to asset dict
            asset_dict[a[0] + parent_name[i]] = id
            continue

        # checks if asset already exists (level 0 assets)
        elif a[2] == "" and (asset_name[i], asset_type_id[i]) in e_0:
            id = [
                x["id"]
                for x in project_assets
                if x["asset_type"]["id"] == a[1] and x["name"] == a[0]
            ]

            if id and type(id) == list:
                id = id[0]

            # replace temp id
            temp_id = asset_dict[a[0] + parent_name[i]]
            for asset in assets["assets"]:  #
                if parent_id:
                    if asset["parent_id"] == temp_id:
                        asset["parent_id"] = id

            # adds id to asset dict
            asset_dict[a[0] + parent_name[i]] = id
            continue

        else:
            asset = {
                "asset_id": asset_ids[i],
                "asset_type_id": asset_type_id[i],
                "project_id": project_ids[i],
                "name": asset_name[i],
            }
            parent_id = asset_dict[parent_name[i]]
            # if parent_name[i]=="Dalkeith RoadProject": print(asset_dict)
            # print(parent_id, parent_name[i])
            if parent_id:
                asset["parent_id"] = parent_id

            assets["assets"].append(asset)

    if assets["assets"]:
        assets["assets"] = sorted(assets["assets"], key=lambda d: d["name"])

        # sort the body by asset_type_id to upload in correct order
        sorted(
            assets["assets"],
            key=lambda item: list(asset_types_map.values()).index(
                item["asset_type_id"]
            ),
        )
        pyddb.post_body(endpoint="assets", body=assets)
    return asset_dict


def upload_parameters(df, project_id, parameter_types, asset_dict, units, source_dict):

    ### Clean Data

    df = df[df["Source Type"] != "no source"]
    df = df[df["Value"] != "no value"]

    parameters = df[
        [
            "Parameter Type",
            "Parent Asset Chain",
            "Asset Name",
            "Value",
            "Unit",
            "Source Type",
            "Source Title",
            "Source Reference",
        ]
    ].values.tolist()

    # all parameters in spreadsheet

    all_parameters = [
        [
            parameter_types[x[0].replace("\xa0", " ")],  # parameter type id
            asset_dict[x[2] + x[1]],  # asset id
            x[3],  # value
            units[x[4]],  # unit id
            source_dict[x[5] + x[6] + x[7]],
        ]  # source id
        for x in parameters
    ]

    all_parameter_types = list(set([x[0] for x in all_parameters]))
    all_asset_ids = list(set([x[1] for x in all_parameters]))

    ### Separate All Parameters into New/Update/Ignore

    existing_items = pyddb.get_parameters(
        project_id=project_id,
        asset_id=all_asset_ids,
        parameter_type_id=all_parameter_types,
        page_limit=99999,
    )

    existing_project_items = pyddb.get_parameters(
        project_id=project_id,
        parameter_type_id=all_parameter_types,
        page_limit=99999,
        project_parameter=True,
    )

    existing_items.extend(existing_project_items)

    """parameters = [x for x in all_parameters               # show every parameter in the spreadsheet
     if [x[0], x[1]] not in                               # if the item (parameter type id, asset id)
     [[x["parameter_type"]["id"], x["parents"][0]["id"]]  # is not in the list of existing items
      for x in existing_items]]                           # for every item that exists"""

    # p type id, asset id, value, unit id , source_id
    existing_item_links = [
        [y["parameter_type"]["id"], y["parents"][0]["id"] if y["parents"] else None]
        for y in existing_items
    ]

    existing_item_all = [
        [
            y["parameter_type"]["id"],
            y["parents"][0]["id"] if y["parents"] else None,
            y["revision"]["values"][0]["value"] if y["revision"] else None,
            # y["revision"]["values"][0]["unit"]["id"] if y["revision"]["values"][0]["unit"] else None,
            y["revision"]["source"]["id"] if y["revision"] else None,
        ]
        for y in existing_items
    ]

    for i, y in enumerate(existing_items):
        if y["revision"]:
            if y["revision"]["values"][0]["unit"]:
                unit_id = y["revision"]["values"][0]["unit"]["id"]
            else:
                unit_id = None
        else:
            unit_id = None
        # print(existing_item_all[i])
        try:
            existing_item_all[i].insert(3, unit_id)
        except AttributeError:
            pass

    existing_ids = [y["id"] for y in existing_items]

    existing_parameters = []
    new_parameters = {"parameters": []}
    ignored = []
    for x in all_parameters:
        if [x[0], x[1]] in existing_item_links:  # if the parameter already exists
            # if [value, unit, source] = value, unit, source
            try:
                if x not in existing_item_all:
                    where = existing_item_links.index([x[0], x[1]])

                    existing_parameters.append([existing_ids[where], x[4], x[2], x[3]])
                else:
                    ignored.append(x)

            except TypeError:
                pass

        else:
            new_parameter = {
                "parameter_type_id": x[0],
                "project_id": project_id,
                "revision": {
                    "source_id": x[4],
                    "comment": "Python Upload",
                    "location_in_source": "Python",
                    "values": [
                        {"value": x[2], "unit_id": None if x[3] == "None" else x[3]}
                    ],
                },
            }
            if x[1]:
                new_parameter["parent_ids"] = x[1]

            new_parameters["parameters"].append(new_parameter)

    ### Post New Parameters
    num_new = len(new_parameters["parameters"])
    l = range(num_new)

    print(f"Posting {num_new} new parameters:")

    batch_size = 5

    chunks = [l[i : i + batch_size] for i in range(0, len(l), batch_size)]
    errors = []

    # print("Batch posting parameters...")
    for i, chunk in enumerate(chunks):
        body = {"parameters": []}
        batch = new_parameters["parameters"][list(chunk)[0] : list(chunk)[-1]]

        body["parameters"] = batch

        if not body == {"parameters": []}:
            res = pyddb.post_body("parameters/", body=body)

            # print(res)
            if "msg" in res:
                print(f"Errors in batch {i}.")
                errors.append(body)
                # print(body)
            else:
                print(f"Batch {i+1} posted successfully.")
    if errors:
        print(
            f"There were errors posting the following ({len(errors)}) bodies: {errors}"
        )
    else:
        if num_new:
            print(f"All parameters posted successfully.")

    ### Post Parameter Updates

    print(f"Updating {len(existing_parameters)} parameters:")

    update_errors = []
    for i in existing_parameters:

        body = {
            "source_id": i[1],
            "values": [
                {
                    "value": i[2],
                    "unit_id": i[3],
                }
            ],
        }

        parameter_id = i[0]
        res = pyddb.post_body(endpoint=f"parameters/{parameter_id}/revision", body=body)

        if "msg" in res:
            update_errors.append(body)
    if errors:
        print(
            f"There were errors posting the following ({len(update_errors)}) bodies: {update_errors}"
        )
    else:
        if existing_parameters:
            print(f"All parameters updated successfully.")


def generate_df(file_name, sheet_names, header_rows=1):
    def prep_sheet(file_name, sheet_name, header_rows):
        df = pd.read_excel(file_name, sheet_name=sheet_name, header=header_rows)
        return df

    columns = [
        "Parent Asset Chain",
        "Asset Type",
        "Asset Name",
        "Parameter Type",
        "Value",
        "Unit",
        "Source Type",
        "Source Title",
        "Source Reference",
        "Source URL",
        "Day",
        "Month",
        "Year",
    ]

    df = pd.DataFrame(columns=columns)

    for sheet in sheet_names:
        df = df.append(prep_sheet(file_name, sheet, header_rows))

    df = df.dropna(how="all")
    df[["Value"]] = df[["Value"]].fillna(value="no value")
    df[["Unit"]] = df[["Unit"]].fillna(value=0)
    df[["Asset Name"]] = df[["Asset Name"]].fillna(value=0)
    df = df[df["Asset Name"] != 0]

    df[["Source URL"]] = df[["Source URL"]].fillna("")

    today = datetime.date.today()
    df[["Day"]] = df[["Day"]].fillna(str(int(float(value=today.day))))
    df[["Month"]] = df[["Month"]].fillna(str(int(float(value=today.day))))
    df[["Year"]] = df[["Year"]].fillna(str(int(float(value=today.day))))

    return df[columns]


def upload_project(job_numbers, df, tag_projects, project_tag):

    (
        source_types,
        tag_types,
        units,
        parameter_types,
        asset_types_map,
    ) = generate_guid_dicts()

    for job_number in job_numbers:

        print(f"Creating project {job_number}\n")
        project = pyddb.Project(job_number)
        project_id = project.project_id
        (
            asset_dict,
            asset_type_ids,
            project_ids,
            asset_names,
            asset_ids,
            parent_names,
            a_name_dict,
        ) = generate_asset_lists(df, project_id, asset_types_map)

        if tag_projects:
            tag_id = tag_types[project_tag]
            project.tag(tag_id)

        print("Posting assets...\n")
        asset_dict = bulk_post_assets(
            asset_dict,
            asset_type_ids,
            project_ids,
            asset_names,
            asset_ids,
            a_name_dict,
            asset_types_map,
            parent_names,
        )
        print("Posting sources...\n")
        source_dict = post_all_sources(df, project_id, source_types)
        print("Posting parameters...\n")
        upload_parameters(
            df, project_id, parameter_types, asset_dict, units, source_dict
        )
