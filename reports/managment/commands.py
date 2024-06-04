import requests
from envparse import Env

from reports.report import get_formatted_year_and_month

Env.read_envfile('env_vars/report.env')
env = Env()

TOKEN = env.str("TOKEN")
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def upload_file(loadfile, savefile, replace=True):
    """Загрузка файла.
    loadfile: Путь к загружаемому файлу
    savefile: Путь к файлу на Диске
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)
            return res


def upload_to_ydisk(month, year):

    loadfile = f'static/reports/report_{month}_{year}.xlsx'  # локальный путь
    savefile = f'report_time_tracking/report_{month}_{year}.xlsx'  # путь на диске
    try:
        upload_file(loadfile, savefile)
    except Exception as e:
        return f'Failed upload file {loadfile}: {e}'
    return f'OK'
