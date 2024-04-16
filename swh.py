import os


import requests

from envparse import Env

env = Env()
# TG_API = env.str("BOT_API_KEY", default="secret_key")
WHOOK = 'hr.petrushkagroup.ru'
TG_API = "6688209134:AAGEDFTzRu2rmfo2MIPdZzKEII9MktFXfYY"
# WHOOK = "eca594b83ea62a.lhr.life"

if __name__ == "__main__":
    r = requests.get(f'https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{WHOOK}/')
    print(r.json())