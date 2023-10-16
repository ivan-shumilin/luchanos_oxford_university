import aiohttp
import subprocess

from swh import TG_API


async def send_messang(text: str):
    data = {
        'chat_id': 369027587,
        'text': text,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'https://api.telegram.org/bot{TG_API}/sendMessage',
                data=data
        ) as response:
            print(response.status)


async def restore_db():
    import os

    folder_path = './dump'
    latest_file = None
    latest_time = 0

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if file_time > latest_time:
                latest_file = filename
                latest_time = file_time

    print(f"The latest file is {latest_file}")

    command = f'pg_restore -U postgres -h 37.140.195.68 -d postgres -c -W dump/{latest_file}'
    subprocess.run(command, shell=True, input=b'postgres\n', stderr=subprocess.PIPE)
