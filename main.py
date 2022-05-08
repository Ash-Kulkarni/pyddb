import sys
from pyddb import *

sys.path.append("../")
from typing import List
from pyddb.models import *
from pyddb.utils.time_function import time_function
from pyddb.utils.download_df import download_df
import asyncio


async def process(project_number: str):
    ddb = DDB()
    [my_project] = await ddb.get_projects(search=project_number)
    assets, parameters, sources, project = await asyncio.gather(
        my_project.assets_df(),
        my_project.parameters_df(),
        my_project.sources_df(),
        my_project.project_df(),
    )

    await asyncio.gather(
        download_df(assets, "assets"),
        download_df(parameters, "parameters"),
        download_df(sources, "sources"),
        download_df(project, "project"),
    )


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process(project_number="11252300"))
