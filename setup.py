from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "DDB API Client"
LONG_DESCRIPTION = "My first Python package with a slightly longer description"

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="pyddb_client",
    version=VERSION,
    author="Ash Dsouza",
    author_email="<youremail@email.com>",
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
    keywords=["python", "first package"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
