from pyddb import DDBClient
from pyddb.models import Parameter


async def delete_parameter(parameter: Parameter):

    response = await DDBClient.delete_request(endpoint=f"parameters/{parameter.id}")
    return response
