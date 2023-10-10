import os


import requests

# from dotenv import load_dotenv


# load_dotenv()
# TG_API = os.getenv('BOT_API_KEY')
# whook = 'hr.petrushkagroup.ru'
TG_API = "6688209134:AAGEDFTzRu2rmfo2MIPdZzKEII9MktFXfYY"
WHOOK = "77a0893f1bb21a.lhr.life"

if __name__ == "__main__":
    r = requests.get(f'https://api.telegram.org/bot{TG_API}/setWebhook?url=https://{WHOOK}/')
    print(r.json())