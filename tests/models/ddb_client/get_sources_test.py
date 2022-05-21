from pyddb import DDB, Source, BaseURL
import pytest

ddb = DDB(url=BaseURL.sandbox)


@pytest.mark.asyncio
async def test_returns_list_of_sources():
    response = await ddb.get_sources(page_limit=1)
    assert isinstance(response, list)
    assert isinstance(response[0], Source)
