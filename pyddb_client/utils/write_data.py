import pickle


async def write_data(filename, data):

    PIK = f"pyddb_client/data/{filename}.dat"

    with open(PIK, "wb") as f:
        pickle.dump(data, f)
