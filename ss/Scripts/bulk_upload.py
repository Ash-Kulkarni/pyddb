import pandas as pd
import datetime
import ddb_get_post as pyddb
import itertools
from typing import List
import uuid
from gooey import Gooey, GooeyParser
import warnings
import sys

# preventing unnecessary errors from excel data validation fields
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# used to show output on gooey console
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)


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
        "": None,
    }
    return asset_types


def generate_guid_dicts():
    """Creates dictionaries of {names:guids} for source type, tag type, units, parameter types, and asset types.

    Asset types are hardcoded with unique names because the names are not unique.
    """
    source_types_map = {
        name: id
        for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_source_types()]
    }

    tag_types_map = {
        name: id for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_tags()]
    }
    tag_types_map["no tag"] = ""  # why is this here

    units_map = {
        name: id for (name, id) in [(x["name"], x["id"]) for x in pyddb.get_units()]
    }
    units_map[0] = None

    parameter_types_res = pyddb.get_parameter_types()

    parameter_types_map = {
        name: id for (name, id) in [(x["name"], x["id"]) for x in parameter_types_res]
    }

    parameter_types_data_type_map = {
        id: data_type
        for (id, data_type) in [
            (x["name"], x["data_type"]) for x in parameter_types_res
        ]
    }

    asset_types_map = get_asset_type_dict()

    return (
        source_types_map,
        tag_types_map,
        units_map,
        parameter_types_map,
        asset_types_map,
        parameter_types_data_type_map,
    )


def generate_df(
    file_name: str, sheet_names: List[str], header_rows: int = 1
) -> pd.DataFrame:
    """Reads xlsx file and returns cleaned DataFrame.

    Combines all given sheets in file, removes empty rows, adds today's date to blank publication dates

    Args:
    file_name : path to xlsx file
    sheet_names: list of sheet names to read
    header_rows: number of rows above data to read - should be same on all sheets"""
    columns = [  # only reads these columns in each sheet
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

    df = pd.concat(  # join all sheets and create dataframe
        [pd.DataFrame(columns=columns)]
        + [
            pd.read_excel(
                file_name,
                sheet_name=sheet_name,
                header=header_rows,
            )
            for sheet_name in sheet_names
        ]
    )[columns]

    df = df.dropna(how="all")  # remove empty rows

    df[["Asset Name"]] = df[["Asset Name"]].fillna(value=0)
    df = df[df["Asset Name"] != 0]  # remove rows without asset names

    df[["Source URL"]] = df[["Source URL"]].fillna("")  # ignore empty source URLs

    # today = datetime.date.today()  # use today's date if no publication date is given - causes many duplicate sources when rerunning script
    # df[["Day"]] = df[["Day"]].fillna(value=str(int(float(today.day))))
    # df[["Month"]] = df[["Month"]].fillna(value=str(int(float(today.month))))
    # df[["Year"]] = df[["Year"]].fillna(value=str(int(float(today.year))))

    df[["Day"]] = df[["Day"]].fillna(value=1)
    df[["Month"]] = df[["Month"]].fillna(value=1)
    df[["Year"]] = df[["Year"]].fillna(value=2020)

    # convert all dates to strings without decimals
    df[["Day"]] = df[["Day"]].astype(float)
    df[["Month"]] = df[["Month"]].astype(float)
    df[["Year"]] = df[["Year"]].astype(float)
    df[["Day"]] = df[["Day"]].astype(int)
    df[["Month"]] = df[["Month"]].astype(int)
    df[["Year"]] = df[["Year"]].astype(int)
    df[["Day"]] = df[["Day"]].astype(str)
    df[["Month"]] = df[["Month"]].astype(str)
    df[["Year"]] = df[["Year"]].astype(str)

    df[["Unit"]] = df[["Unit"]].fillna(value=0)  # Unitless entries set to 0

    # clean asset columns
    df[["Asset Type"]] = df[["Asset Type"]].fillna(value="")
    df[["Parent Asset Chain"]] = df[["Parent Asset Chain"]].fillna(value="")

    return df


def upload_project(job_number):
    """Posts project to DDB, return project_id."""
    print(f"Creating project {job_number}\n")
    project = pyddb.Project(job_number)
    return project.project_id


def post_all_sources(df, project_id, source_types_map):
    """Posts all sources in DataFrame.

    Removes sources missing a type, title, or reference.
    Removes duplicates.
    Posts all sources if another source with the same type, title, reference, and url doesn't already exist.

    Returns:
        A dict of {[source details]: source_id}"""
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
    ]

    gross_sources = gross_sources.dropna(
        subset=["Source Type", "Source Title", "Source Reference"]
    )  # remove any sources if either of these three are missing

    gross_sources_list = gross_sources.values.tolist()

    mod = "1246633d-9e75-4fcd-ba0e-0513ff24ed37"

    sources = [
        x.split(mod)
        for x in list(
            set([mod.join([str(y) for y in x]) for x in gross_sources_list])
        )  # remove duplicate sources
    ]

    source_type_list, *other_source_details = list(zip(*sources))

    source_type_id_list = [
        source_types_map[source_type] for source_type in source_type_list
    ]

    keys = ["".join(source) for source in sources]
    values = pyddb.add_new_source(
        project_id,
        source_type_id_list,
        *[[*s] for s in other_source_details],
    )

    source_dict = dict(zip(keys, values))
    return source_dict


def generate_asset_lists(df, asset_types_map):
    """Generates lists of asset types, project ids, asset names, asset ids, and parent names.

    Takes the dataframe from the bulk upload template and a project_id.
    Reads the asset-related columns, removes any blanks, project rows, and duplicates.
    Creates a dictionary of all assets and generates GUIDs for them.
    """
    df = df[df["Asset Name"] != "Project"]

    # Remove duplicates
    asset_list = df[["Asset Type", "Asset Name", "Parent Asset Chain"]].values.tolist()
    asset_list.sort()
    asset_list = list(asset_list for asset_list, _ in itertools.groupby(asset_list))
    asset_dict = {"Project": None}
    # sort assets into asset hierarchy order
    asset_list.sort(
        key=lambda item: list(asset_types_map.keys()).index(item[0]),
    )

    # create list of asset types, names, ids, parents
    asset_types, asset_names, _ = list(map(list, zip(*asset_list)))
    asset_type_ids = [asset_types_map[asset_type] for asset_type in asset_types]

    # generate dict of assets and new guids for them

    for asset in asset_list:
        asset_dict[asset[1] + asset[2]] = str(uuid.uuid4())

    asset_ids = [asset_dict[asset[1] + asset[2]] for asset in asset_list]
    parent_names = [asset[2] for asset in asset_list]

    # generate dict of {parent asset chain : asset name}
    asset_name_dict = {asset[1] + asset[2]: asset[1] for asset in asset_list}
    asset_name_dict["Project"] = "Project"

    return (
        asset_dict,
        asset_type_ids,
        asset_names,
        asset_ids,
        parent_names,
        asset_name_dict,
    )


def bulk_post_assets(
    df,
    project_id: str,
    asset_types_map: dict,
):
    """Uploads lists of assets.

    Takes a dictionary of asset names and GUIDs, lists of asset type ids,
    project ids, asset names, asset ids, and parent asset names.

    Checks for existing assets, adds their ids to the dictionary.
    Constructs a body of all new assets and posts them.

    Returns:
        Dictionary of asset names and GUIDS.
    """
    # check if there are assets
    if any(df["Asset Type"].values.tolist()):
        (
            asset_dict,
            asset_type_ids,
            asset_names,
            asset_ids,
            parent_names,
            asset_name_dict,
        ) = generate_asset_lists(df, asset_types_map)

        # get all assets on the project and build a dictionary of their names and GUIDS.
        project_assets = pyddb.get_assets(project_id=project_id)
        existing_asset_dict = {
            id: name for (id, name) in [(x["id"], x["name"]) for x in project_assets]
        }
        existing_asset_dict[None] = "Project"

        # list of all existing assets
        existing_asset_list = [
            [
                existing_asset["name"],
                existing_asset["asset_type"]["id"],
                existing_asset_dict[existing_asset["parent"]],
            ]
            for existing_asset in project_assets
        ]

        # print(existing_asset_list)
        assets = {"assets": []}

        # for every asset we're uploading
        for i, _ in enumerate(asset_type_ids):
            asset = [
                asset_names[i],
                asset_type_ids[i],
                asset_name_dict[parent_names[i]],
            ]

            # checks if asset already exists
            if asset in existing_asset_list:

                id = [
                    project_asset["id"]
                    for project_asset in project_assets
                    if project_asset["asset_type"]["id"] == asset[1]
                    and project_asset["name"] == asset[0]
                    and existing_asset_dict[project_asset["parent"]]
                    == asset_name_dict[parent_names[i]]
                ]

                if id and type(id) == list:
                    id = id[0]

                # adds id to asset dict
                asset_dict[asset[0] + parent_names[i]] = id
                continue

            # checks if asset already exists (level 0 assets)
            elif asset[2] == "" and [asset_names[i], asset_type_ids[i]] in [
                asset[:1] for asset in existing_asset_list
            ]:
                id = [
                    project_asset["id"]
                    for project_asset in project_assets
                    if project_asset["asset_type"]["id"] == asset[1]
                    and project_asset["name"] == asset[0]
                ]

                if id and isinstance(id, list):
                    id = id[0]

                # replace generated asset guid with existing asset guid
                temp_id = asset_dict[asset[0] + parent_names[i]]
                # for asset in assets["assets"]:  #
                #     if parent_id:
                #         if asset["parent_id"] == temp_id:
                #             asset["parent_id"] = id

                # adds id to asset dict
                asset_dict[asset[0] + parent_names[i]] = id
                continue

            # if the asset does not exist
            else:
                asset = {
                    "asset_id": asset_ids[i],
                    "asset_type_id": asset_type_ids[i],
                    "project_id": project_id,
                    "name": asset_names[i],
                }
                parent_id = asset_dict[parent_names[i]]

                if parent_id:
                    asset["parent_id"] = parent_id

                assets["assets"].append(asset)

        if assets["assets"]:

            pyddb.post_body(endpoint="assets", body=assets)
    else:
        asset_dict = {"Project": None}
    return asset_dict


def upload_parameters(
    df,
    project_id,
    parameter_types_map,
    asset_dict,
    units_map,
    source_dict,
    parameter_types_data_type_map,
    debug=False,
):

    batch_size = 2 if debug else 30
    ### Clean Data
    df = df.dropna(how="any")
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
            "Source URL",
            "Day",
            "Month",
            "Year",
        ]
    ].values.tolist()

    def convert_to_bool(value) -> bool:
        if str(value).lower() in ["1", "true"]:
            return True
        elif str(value).lower() in ["0", "false"]:
            return False
        else:
            return None

    for i, x in enumerate(parameters.copy()):
        if parameter_types_data_type_map[x[0]] == "boolean":
            parameters[i][3] = convert_to_bool(x[3])
        elif parameter_types_data_type_map[x[0]] == "number":
            parameters[i][3] = float(x[3])
        elif parameter_types_data_type_map[x[0]] == "string":
            parameters[i][3] = str(x[3])
        elif parameter_types_data_type_map[x[0]] == "integer":
            parameters[i][3] = int(x[3])

    # all parameters in spreadsheet

    all_parameters = [
        [
            parameter_types_map[x[0].replace("\xa0", " ")],  # parameter type id
            asset_dict[x[2] + x[1]],  # asset id
            x[3],  # value
            units_map[x[4]],  # unit id
            source_dict["".join([str(y) for y in x[5:12]])],
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

    """parameters = [x for x in all_parameters            # show every parameter in the spreadsheet
     if [x[0], x[1]] not in                               # if the item (parameter type id, asset id)
     [[x["parameter_type"]["id"], x["parents"][0]["id"]]  # is not in the list of existing items
      for x in existing_items]]                           # for every item that exists"""

    # p type id, asset id, value, unit id , source_id
    existing_item_links = [
        [
            item["parameter_type"]["id"],
            item["parents"][0]["id"] if item["parents"] else None,
        ]
        for item in existing_items
    ]

    existing_item_all = [
        [
            item["parameter_type"]["id"],
            item["parents"][0]["id"] if item["parents"] else None,
            item["revision"]["values"][0]["value"] if item["revision"] else None,
            # y["revision"]["values"][0]["unit"]["id"] if y["revision"]["values"][0]["unit"] else None,
            item["revision"]["source"]["id"] if item["revision"] else None,
        ]
        for item in existing_items
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

    print(f"Posting {num_new} new parameter(s):")

    # batch_size = 1

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
            res = pyddb.post_body("parameters/", body=body)

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


def main(file, job_number, env="sandbox", header_rows=1, debug=False):

    pyddb.site = env

    settings_df = pd.read_excel(file, sheet_name="DDB Bulk Upload Settings")
    sheet_names = settings_df["Sheet Names"].values.tolist()
    header_rows = int(float(settings_df["Header Rows"].values.tolist()[0]))
    settings_df["Tag Name"] = settings_df["Tag Name"].fillna(0)
    tag_names = settings_df["Tag Name"].values.tolist()

    print("Reading file...")
    df = generate_df(
        file_name=file,
        sheet_names=sheet_names,
        header_rows=header_rows,
    )

    print("Converting contents...")
    (
        source_types_map,
        tag_types_map,
        units_map,
        parameter_types_map,
        asset_types_map,
        parameter_types_data_type_map,
    ) = generate_guid_dicts()

    print("Searching for project...")
    project_id = upload_project(job_number=job_number)

    if tag_names:
        print("Tagging project...")
        for tag_name in tag_names:
            if tag_name:
                try:
                    pyddb.tag_project(
                        project_id=project_id, tag_id=tag_types_map[tag_name]
                    )
                except KeyError:
                    print(
                        f"There is an error in the tag name: {tag_name}.  Project tagging failed."
                    )
    print("Posting sources...")
    source_dict = post_all_sources(
        df=df, project_id=project_id, source_types_map=source_types_map
    )

    print("Posting assets...")
    asset_dict = bulk_post_assets(
        df=df, project_id=project_id, asset_types_map=asset_types_map
    )

    print("Posting parameters...")
    upload_parameters(
        df=df,
        project_id=project_id,
        parameter_types_map=parameter_types_map,
        asset_dict=asset_dict,
        units_map=units_map,
        source_dict=source_dict,
        parameter_types_data_type_map=parameter_types_data_type_map,
        debug=debug,
    )


@Gooey(program_name="DDB Upload")
def upload():
    parser = GooeyParser(description="Upload Data to Digital Design Brief")
    subparsers = parser.add_subparsers(required=True)
    uploader = subparsers.add_parser("upload", help="Upload Project")

    uploader.add_argument(
        "environment",
        widget="FilterableDropdown",
        nargs="*",
        help="Select Environment - Production, Sandbox, or Development",
        default="",
        choices=["prod", "sandbox", "dev"],
        metavar="DDB Environment",
    )
    uploader.add_argument(
        "File",
        widget="FileChooser",
        help="Select File to Upload",
    )
    uploader.add_argument(
        "job_number",
        help="8 Digit Project Number",
        metavar="Project Number",
        default=11252300,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = upload()

    main(
        file=args.File,
        job_number=args.job_number,
        env=args.environment[0],  # "11252300",
        debug=True,
    )
