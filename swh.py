import os


import requests

from envparse import Env

Env.read_envfile('env_vars/.env')
env = Env()

WHOOK = env.str("WHOOK")
TG_API = env.str("TG_API")

if __name__ == "__main__":
    r = requests.get(f'https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{WHOOK}/')
    print(r.json())