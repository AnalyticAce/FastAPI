import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY') or None
if SECRET_KEY is None:
    raise ValueError('No SECRET_KEY set for FastAPI application')

ALGORITHM = os.environ.get('ALGORITHM')
if ALGORITHM is None:
    raise ValueError('No ALGORITHM set for FastAPI application')

ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise ValueError('No ACCESS_TOKEN_EXPIRE_MINUTES set for FastAPI application')

MONGO_CONNECTION_STRING = os.environ.get('MONGO_CONNECTION_STRING')
if MONGO_CONNECTION_STRING is None:
    raise ValueError('No MONGO_CONNECTION_STRING set for FastAPI application')

MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
if MONGO_DB_NAME is None:
    raise ValueError('No MONGO_DB_NAME set for FastAPI application')

MONGO_COLLECTION_NAME_USER = os.environ.get('MONGO_COLLECTION_NAME_USER')
if MONGO_COLLECTION_NAME_USER is None:
    raise ValueError('No MONGO_DB_COLLECTION set for FastAPI application')