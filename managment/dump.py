import os
import subprocess
from datetime import date

from envparse import Env
from loguru import logger

from managment.commands import upload_to_ydisk

Env.read_envfile('env_vars/postgres.env')
env = Env()

POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_HOST = env.str("POSTGRES_HOST")
POSTGRES_PORT = env.str("POSTGRES_PORT")


async def load_dump(dump_file) -> str:
    savefile = f"backup/{dump_file}"
    loadfile = f"dumps/{dump_file}"
    response = await upload_to_ydisk(loadfile, savefile)
    return response


async def dump_db():
    """Делает дамп базы данных в формате tar"""
    current_time = date.today()
    dump_file = f"dump_{current_time.year}_{current_time.month}_{current_time.day}.tar"
    logger.info(f"дамп базы данных в файл {dump_file}")
    command = f"pg_dump -U {POSTGRES_USER} -h {POSTGRES_HOST} -p {POSTGRES_PORT} -E UTF8 -F tar -f dumps/{dump_file} {POSTGRES_DB}"
    os.environ['PGPASSWORD'] = POSTGRES_PASSWORD
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as err:
        logger.error(err)
        return err
    response = await load_dump(dump_file)
    return response
