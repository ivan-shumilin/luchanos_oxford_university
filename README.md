# luchanos_oxford_university
p3d%s$*V=-Pa

data base:
имя бд: time_tracking
пользователь: admin
пароль: asDSqwBF23*

Для поднятия сервисов баз для локальной разработки нужно запустить команду:

```
make up
```

Для накатывания миграций, если файла alembic.ini ещё нет, нужно запустить в терминале команду:

```
alembic init migrations
```

После этого будет создана папка с миграциями и конфигурационный файл для алембика.

- В alembic.ini нужно задать адрес базы данных, в которую будем катать миграции.
- Дальше идём в папку с миграциями и открываем env.py, там вносим изменения в блок, где написано

```
from myapp import mymodel
```

- Дальше вводим: ```alembic revision --autogenerate -m "comment"``` - делается при любых изменениях моделей
- Будет создана миграция
- Дальше вводим: ```alembic upgrade heads```

Для того, чтобы во время тестов нормально генерировались миграции нужно:
- сначала попробовать запустить тесты обычным образом. с первого раза все должно упасть
- если после падения в папке tests создались алембиковские файлы, то нужно прописать туда данные по миграхам
- если они не создались, то зайти из консоли в папку test и вызвать вручную команды на миграции, чтобы файлы появились

Локально:
```ssh -R 80:localhost:8000 nokey@localhost.run```

Вознкла проблема, при создании init миграции она была пустая.
удалить базу:
sudo dropdb -U postgres -h 0.0.0.0 postgres
нужно убить процессы с пользователем shumilin
sudo lsof -i :5432

Потом создать базу
createdb -U postgres -h 0.0.0.0 postgres

И сделать первую миграцию init:
```
alembic init migrations
```
При make makemigrations в файлу alembic.ini должно быть раскоментировано 
# local
sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5432/postgres

Поменять .env
- Дальше вводим: ```alembic revision --autogenerate -m "comment"``` - делается при любых изменениях моделей
- Будет создана миграция
- Дальше вводим: ```alembic upgrade heads```


Для удаления всех таблиц из БД postgres можно выполнить следующие шаги:
1. Откройте командную строку или терминал и подключитесь к БД postgres:
psql -U username -d dbname
где username - имя пользователя БД, а dbname - имя БД.
2. Выполните следующую команду для получения списка всех таблиц в БД:
\dt
3. Для удаления всех таблиц выполните следующую команду:
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
Эта команда удалит схему public со всеми таблицами и создаст новую пустую схему public. Обратите внимание, что все данные в таблицах будут безвозвратно удалены, поэтому перед выполнением этой команды убедитесь, что вы действительно хотите удалить все таблицы из БД.

pg_restore --clean --dbname=postgresql://admin:asDSqwBF23*@79.174.88.60:19832/time_tracking -v ./2023-10-31__23-59__backup.sql
55.805155:37.520674

---

## ENVs

Всего должно быть определено 3 среды в папке ./env_vars:

1. **.env** 

Содержит:

+ APP_PORT
+ BOT_API_KEY
+ SENTRY_URL

+ REAL_DATABASE_URL
+ TEST_DATABASE_URL

+ SECRET_KEY
+ ALGORITHM

+ ACCESS_TOKEN_EXPIRE_MINUTES

+ TG_API
+ WHOOK

2. **postgres.env** - используется в docker-compose-*.yaml

Содержит: 
+ POSTGRES_USER
+ POSTGRES_PASSWORD
+ POSTGRES_DB

3. **postgres-local.env** - используется в docker-compose-local.yaml

Содержит:

+ POSTGRES_USER
+ POSTGRES_PASSWORD
+ POSTGRES_DB
