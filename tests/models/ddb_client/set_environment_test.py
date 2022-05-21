from pyddb import DDB, BaseURL


def test_url_changes():
    # assuming default environment is sandbox
    ddb = DDB(url=BaseURL.sandbox)
    assert ddb.url == "https://sandbox.ddb.arup.com/api/"
    ddb = DDB(url=BaseURL.dev)
    assert ddb.url == "https://dev.ddb.arup.com/api/"


def test_url_changes_in_methods():
    # assuming default environment is sandbox
    ddb = DDB(url=BaseURL.sandbox)
    sandbox_projects = ddb.get_projects()
    ddb = DDB(url=BaseURL.dev)
    dev_projects = ddb.get_projects()
    assert sandbox_projects != dev_projects
