import pandas as pd


async def download_df(df: pd.DataFrame, name: str):

    df.to_csv(f"{name}.csv", index=False)
    print(f"Dataframe saved as {name}.csv")
    return
