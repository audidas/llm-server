import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class DatabaseConfig:
    NAME = os.environ["DATABASE_NAME"]
    HOST = os.environ["DATABASE_HOST"]
    PORT = os.environ["DATABASE_PORT"]
    USER_NAME = os.environ["DATABASE_USER_NAME"]
    USER_PASSWORD = os.environ["DATABASE_USER_PASSWORD"]

    URL = f"mongodb://{USER_NAME}:{USER_PASSWORD}@{HOST}:{PORT}"
   


class JWTConfig:
    ALGORITHM = os.environ["JWT_ALGORITHM"]

    ACCESS = os.environ["JWT_ACCESS"]  # "acc"
    ACCESS_KEY = os.environ["JWT_ACCESS_KEY"]
    ACCESS_EXPIRED_AT = os.environ["JWT_ACCESS_EXPIRED_AT"]  # sec

    REFRESH = os.environ["JWT_REFRESH"]  # "ref"
    REFRESH_KEY = os.environ["JWT_REFRESH_KEY"]
    REFRESH_EXPIRED_AT = os.environ["JWT_REFRESH_EXPIRED_AT"]  # sec


class LLMConfig:
    PROTOCOL = os.environ["LLM_SERVER_PROTOCOL"]
    SERVER = os.environ["LLM_SERVER"]
    PATH = os.environ["LLM_SERVER_PATH"]


class RedisConfig:
    HOST = os.environ["REDIS_HOST"]
    PORT = os.environ["REDIS_PORT"]
    PASSWORD = os.environ["REDIS_PASSWORD"]


class S3Config:
    BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
    AWS_ACCESS = os.environ["AWS_ACCESS_KEY"]
    AWS_SECRET = os.environ["AWS_SECRET_KEY"]
    REGION = os.environ["AWS_REGION"]
