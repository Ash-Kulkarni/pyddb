from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "DDB API Client"
LONG_DESCRIPTION = "Python interface for interacting with the Digital Design Brief REST API."

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="pyddb",
    version=VERSION,
    author="Ash Kulkarni",
    author_email="<ash.kulkarni@arup.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "aiohttp",
        "asyncio",
    ],
    dependency_links=[
        "https://github.com/arup-group/ddbpy_auth/tarball/master"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    keywords=["python", "ddb", "digital", "design", "brief", "client", "api"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
