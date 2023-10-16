import aiohttp

from swh import TG_API


async def send_messang():
    data = {
        'chat_id': 369027587,
        'text': "Ошибка сервера",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'https://api.telegram.org/bot{TG_API}/sendMessage',
                data=data
        ) as response:
            print(response.status)
