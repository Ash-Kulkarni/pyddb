from pyddb.utils.regenerate_all_types import regenerate_all_types


async def main():
    await regenerate_all_types()


import asyncio

asyncio.run(main())
