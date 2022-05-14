from pyddb import DDB


def test_environment_changes():
    # assuming default environment is sandbox
    ddb = DDB()
    assert ddb.environment == "sandbox"
    ddb.set_environment("dev")
    assert ddb.environment == "dev"


def test_url_changes():
    # assuming default environment is sandbox
    ddb = DDB()
    assert ddb.url == "https://sandbox.ddb.arup.com/api/"
    ddb.set_environment("dev")
    assert ddb.url == "https://dev.ddb.arup.com/api/"


def test_url_changes_in_methods():
    # assuming default environment is sandbox
    ddb = DDB()
    ddb.set_environment("sandbox")
    sandbox_projects = ddb.get_projects()
    ddb.set_environment("dev")
    dev_projects = ddb.get_projects()
    assert sandbox_projects != dev_projects
