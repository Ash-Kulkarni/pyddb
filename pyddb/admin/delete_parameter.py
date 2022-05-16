from pyddb import DDBClient, Parameter


async def delete_parameter(parameter: Parameter):

    response = await DDBClient.delete_request(endpoint=f"parameters/{parameter.id}")
    return response
