import asyncio

import aiohttp


async def main():

    async with aiohttp.ClientSession() as session:
        # response = await session.post(
        #     "http://127.0.0.1:8080/advertisement",
        #     json={
        #       "heading": "Продам машину Nexia",
        #       "description": "Классика на 13 бубликах",
        #       "owner": "Михеев и Павлов +9120007653"
        #     }
        # )
        # print(response.status)
        # print(await response.json())

        # response = await session.get(
        #     "http://127.0.0.1:8080/advertisement/1",
        # )
        # print(response.status)
        # print(await response.json())


        response = await session.delete(
            "http://127.0.0.1:8080/advertisement/1",
        )
        print(response.status)
        print(await response.json())

        response = await session.get(
            "http://127.0.0.1:8080/advertisement/1",
        )
        print(response.status)
        print(await response.json())


asyncio.run(main())
