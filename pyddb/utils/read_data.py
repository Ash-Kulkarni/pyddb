import pickle


async def read_data(filename):

    PIK = f"pyddb_client/data/{filename}.dat"

    with open(PIK, "rb") as f:
        return pickle.load(f)
