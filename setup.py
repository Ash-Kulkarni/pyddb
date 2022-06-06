from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "DDB API Client"
LONG_DESCRIPTION = (
    "Python interface for interacting with the Digital Design Brief REST API."
)


setup(
    name="pyddb",
    version=VERSION,
    author="Ash Kulkarni",
    author_email="<ash.kulkarni@arup.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["pydantic", "aiohttp", "pandas", "ipykernel"],
    dependency_links=["https://github.com/arup-group/ddbpy_auth/tarball/master"],
    keywords=["python", "ddb", "digital", "design", "brief", "client", "api"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
