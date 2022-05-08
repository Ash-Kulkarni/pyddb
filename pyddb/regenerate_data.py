from utils import regenerate_all_types, read_data
import asyncio


async def main():
    data = read_data("source_types")
    print(data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(regenerate_all_types())
