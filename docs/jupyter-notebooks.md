# Digital Design Brief - Jupyter Notebooks

## Virtual Environment Setup

To ensure you're using the virtual environment, you'll need to create a virtual environment, activate it, and the create a kernel using the virtual environment. You can then launch notebooks from within the environment.

```python
python -m venv .venv
.venv/Scripts/activate
pip install git+https://github.com/arup-group/ddbpy_auth.git
pip install git+https://github.com/Ash-Kulkarni/pyddb.git
ipython kernel install --user --name=venv
jupyter notebook
```

To run these notebooks after this initial installation, the run the following commands to activate the virtual environment and launch the notebooks:

```python
.venv/Scripts/activate
jupyter notebook
```

Within the notebook, you can navigate to the `kernel` tab, and select it.

## Imports

First you should import the necessary libraries.
This will likely prompt you for Arup authentication.

```python
import pyddb
import asyncio
```

## Getting Started

All python scripts using the `pyddb` library can be executed in a notebook with only a couple of extra lines.

Notebooks have an event loop running in the background, so we can just nest another as a workaround.

```python
import nest_asyncio
nest_asyncio.apply()
```

### Asynchronous functions

This library uses `asyncio` and `aiohttp`.
You can use the type hints and doc strings for additional information as necessary.

### Initialising the DDB client

The following function shows a typical example of initialising the DDB Client object and setting the environment you're looking to work in.

```python
async def main():
    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)
    projects = await ddb.get_projects()
    return projects

asyncio.run(main())
```

### Storing and Loading DDB Types

To prevent constantly querying the server for information about parameter types, asset types, or other similar information, we can download all of this information and load it as necessary. This is much quicker, and there are methods to query by id or by name.

The following command will download all types, convert them to objects, then pickle them into a local file that you can quickly load as necessary.

```python
asyncio.run(pyddb.regenerate_all_types())
```

In the following example, we're loading these types back in, showing off the different ways they can be loaded.

```python
async def main():

    # you can get a single parameter by name or id:
    area = pyddb.get_parameter_type_by_name("Area")
    volume = pyddb.get_parameter_type_by_id("fdb85750-6c8a-4033-94e4-d91d5825e788")

    print(area)
    print(volume)

asyncio.run(main())
```

```python
async def main():

    # you can get parameters by name or id in a single API call:
    area, volume = pyddb.get_parameter_types_by_name(["Area", "Volume"])

asyncio.run(main())
```

All of this can be applied to parameter types, asset types, source types, tags, or units:

```python
async def main():

    asset_type_site = pyddb.get_asset_type_by_name("site")
    source_type_derived_value = pyddb.get_source_type_by_name("Derived Value")
    tag_cladding = pyddb.get_tag_by_name("Cladding")
    unit_m3 = pyddb.get_unit_by_name("m³")

asyncio.run(main())
```

### Getting and Posting Projects

A posted project will return the project even if it already exists, much like the get project method.

When getting projects, the search keyword can be used to retreive a list of projects by job number, job name, project manager, or project director.

Note that the keyword 'page_limit' should be entered if you want to retreive over 100 projects.

```python
async def main():
    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    post_project = await ddb.post_project(project_number="21515700")
    [get_project] = await ddb.get_projects(search="21515700")

asyncio.run(main())
```

### Getting and Posting Assets

#### Getting Assets

To get assets, we can call the method at DDB, Project, or Asset level to get all assets within the environment, project, or children of a particular asset.

There are also other arguments that can be passed in such as 'asset_type_id' or 'descendants_of' to filter to a specific asset type or all assets below a given asset in the tree.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    [project] = await ddb.get_projects(search="21515700")

    ddb_sandbox_assets = await ddb.get_assets()
    project_sites = await project.get_assets(asset_type_id = pyddb.get_asset_type_by_name("site").id)
    site_child_assets = await project_sites[0].get_assets()

asyncio.run(main())
```

#### Posting Asset Trees

To post many assets in a tree structure, you can define each asset as shown below.

The `parent` parameter must be an `Asset` or `NewAsset` object, and can refer to an existing asset or a new one.
If you specify a new asset as a parent while one already exists in its place, it will update the existing asset instead.

Note that in the following example I am creating the variable and assigning it during this expression using the `:=` operator.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    project = await ddb.post_project(project_number="21515700")

    new_assets = [
        my_site := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("site"),
            name="My DDB Site",
            parent=None,
        ),
        my_building := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("building"),
            name="My DDB Building",
            parent=my_site,
        ),
        my_space_type := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space type"),
            name="MY DDB Space Type",
            parent=my_building,
        ),
        my_first_space_instance := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space instance"),
            name="My First DDB Space Instance",
            parent=my_space_type,
        ),
        my_second_space_instance := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space instance"),
            name="My Second DDB Space Instance",
            parent=my_space_type,
        ),
    ]
    newly_posted_assets = await project.post_assets(assets=new_assets)

asyncio.run(main())
```

### Getting and Posting Sources

#### Getting Sources

To get sources, we can call the method at DDB, or Project level to get all sources within the environment or project.

There are also other arguments that can be passed in such as 'source_type_id', 'title', or 'reference' to filter to a specific source type or all sources matching other criteria.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    [project] = await ddb.get_projects(search="21515700")

    # ddb_sandbox_sources = await ddb.get_sources()
    project_sources = await project.get_sources()

    # print(ddb_sandbox_sources)
    print(project_sources)
asyncio.run(main())
```

#### Posting Sources

To post multiple sources, we can create a list of NewSource objects as shown below and use the Project method to pose them.

If you specify a source that already exists, no duplicate will be created.

This method will also return these back as Source objects.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    [project] = await ddb.get_projects(search="21515700")
    [new_source] = await project.post_sources(
        sources=[
            pyddb.NewSource(
                source_type=pyddb.get_source_type_by_name("Derived Value"),
                title="My source title",
                reference="My source reference",
            )
        ]
    )
    print(new_source)


asyncio.run(main())

```

### Getting and Posting Parameters

#### Getting Parameters

To get parameters, we can call the method at DDB, Project, or Asset level to get all sources within the environment or project.

There are also other arguments that can be passed in such as 'source_type_id', 'title', or 'reference' to filter to a specific source type or all sources matching other criteria.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    [project] = await ddb.get_projects(search="21515700")

    # ddb_sandbox_parameters = await ddb.get_parameters()
    project_parameters = await project.get_parameters()

    # print(ddb_sandbox_parameters)
    print(project_parameters)
asyncio.run(main())
```

#### Posting Parameters

To post parameters, you will first need an asset or project to assign them to. If you're posting them with revisions (values), you'll also need a source for the revision.

You can get these assets or sources as shown previously. This is what I've done in the example below.

I've defined a list of NewParameter objects, with NewRevision objects as their revision properties.

These can be posted as DDB level, but don't curently return Parameter objects back. I might add this in the future.

```python
async def main():

    ddb = pyddb.DDB(url=pyddb.BaseURL.sandbox)

    [project] = await ddb.get_projects(search="21515700")

    """posting a new source"""
    [new_source] = await project.post_sources(
        sources=[
            pyddb.NewSource(
                source_type=pyddb.get_source_type_by_name("Derived Value"),
                title="My source title",
                reference="My source reference",
            )
        ]
    )
    """posting new assets"""
    new_assets = [
        my_site := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("site"),
            name="My DDB Site",
            parent=None,
        ),
        my_building := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("building"),
            name="My DDB Building",
            parent=my_site,
        ),
        my_space_type := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space type"),
            name="MY DDB Space Type",
            parent=my_building,
        ),
        my_first_space_instance := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space instance"),
            name="My First DDB Space Instance",
            parent=my_space_type,
        ),
        my_second_space_instance := pyddb.NewAsset(
            asset_type=pyddb.get_asset_type_by_name("space instance"),
            name="My Second DDB Space Instance",
            parent=my_space_type,
        ),
    ]

    """selecting an asset"""
    newly_posted_assets = await project.post_assets(assets=new_assets)
    my_newly_post_building = next(
        x for x in newly_posted_assets if x.name == "My First DDB Space Instance"
    )

    """posting new parameters"""
    new_parameters = [
        pyddb.NewParameter(
            parameter_type=pyddb.get_parameter_type_by_name("Area"),
            revision=pyddb.NewRevision(
                value=20, unit=pyddb.get_unit_by_name("m²"), source=new_source
            ),
            parent=my_newly_post_building,
        )
    ]

    await ddb.post_parameters(project=project, parameters=new_parameters)


asyncio.run(main())
```
