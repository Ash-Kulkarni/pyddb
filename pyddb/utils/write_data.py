import pickle
from pathlib import Path


async def write_data(filename, data):
    Path("data").mkdir(parents=True, exist_ok=True)
    PIK = f"data/{filename}.dat"

    with open(PIK, "wb") as f:
        pickle.dump(data, f)
