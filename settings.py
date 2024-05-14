"""File with settings and configs for the project"""
from envparse import Env

Env.read_envfile('env_vars/.env')
env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
)  # connect string for the real database
APP_PORT = env.int("APP_PORT")

SECRET_KEY: str = env.str("SECRET_KEY")
ALGORITHM: str = env.str("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES")
SENTRY_URL: str = env.str("SENTRY_URL")

# test envs
TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL"
)  # connect string for the test database