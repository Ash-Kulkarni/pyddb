# DDB API Client for Python

Full documentation of the `pyddb` python package, which simplifies access to the DDB API using Python.

I'll be packaging this correctly in the following weeks.

`pyddb` is my personal library that I've built to access the [DDB API](https://sandbox.ddb.arup.com/documentation) from your Python applications. It provides useful features like posting and updating assets and parameters dynamically, retrieving asset and parameter types without referencing GUIDs, and convenience functions that improve the experience of using the DDB API.

- [Quick Start](#quick-start)
  - [Getting data](#getting-data)
  - [Posting data](#posting-data)
- [Features](#features)
  - [Automatically checks existing data](#automatically-checks-existing-data)
  - [Intuitive wrapper functions](#intuitive-wrapper-functions)
  - [Download DDB types](#download-ddb-types)
- [Usage concepts](#usage-concepts)

## Installation

Requires Python 3.7+

You will first need to install the DDBpy_auth library.

```python
pip install git+https://github.com/arup-group/ddbpy_auth.git
```

You can install the client from its [GitHub listing](https://github.com/arup-group/pyddb) using:

```python
pip install git+https://github.com/Ash-Kulkarni/pyddb
```

## Quick Start

### Getting Data

```python
from pyddb import DDB

# instantiate client and prompt user for arup credentials
ddb = DDB()

# retreive a project from ddb
my_project = await ddb.get_project_by_number(12345678)

# retreive all parameters on the project
project_parameters = await my_project.get_parameters()

# retreive all assets on the project
project_assets = await my_project.get_assets()

# retreive all sources on the project
project_sources = await my_project.get_sources()
```

Each of these are objects with rich metadata. For example, each parameter has detailed parameter type, parent asset, and revision properties.

### Posting Data

```python
from pyddb import DDB

# instantiate client and prompt user for arup credentials
ddb = DDB()

# post and retreive a project from ddb
my_project = await ddb.post_project(12345678)

# retreive a parameter type by name
parameter_type_area = await ddb.get_parameter_type(
	search="Area"
)

# post and retreive a list of new parameters at project level
# revisions are optional and require a value, unit, and source
# existing parameters will have new revisions posted if there is any change
[my_parameters] = await my_project.post_parameters(
	parameters = [
		NewParameter(
			parameter_type = parameter_type_area
			)
		],
	)

# retreive all asset types
asset_types = await ddb.get_asset_types()

asset_type_site = next((a for a in asset_types if a.name == "site"), None)

# post and retreive a list of assets on the project
[my_site] = await my_project.post_assets(
	assets = [
		NewAsset(
			asset_type = asset_type_site,
			name = "My New Site"
			)
		]
	)
```

Each of these post methods will return what they are posting and do not add duplicate data. We need to get the parameter types/asset types/source types/units before posting and do so by name or id. All posts are asynchronous and batched.

## Features

Besides greatly simplifying the process of querying the DDB API, the client provides other useful features.

### Automatically checks existing data

The client checks all existing data before posting to ensure data quality is maintained, posting only the changes, and preventing duplicates.

### Intuitive wrapper functions

The functions for posting parameters understand that if you are posting a new value to an existing parameter, you're really adding a new revision and will access the appropriate endpoint for you.

### Download DDB types

There are functions to download all of our parameter types, asset types, units, and other objects, then load them in by name or uuid. This makes it possible to search for existing data without unnecessary database queries, and we can search by name or uuid.

## Usage concepts

The `pyddb` interface follows a generic pattern that is applicable to a wide variety of uses. In the following example I'll show a script that performs a few processes to size a cold water storage tank for a number of residential blocks.

You can find this example within the **_examples_** subdirectory.
