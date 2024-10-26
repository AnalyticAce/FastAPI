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

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
if GITHUB_CLIENT_ID is None:
    raise ValueError('No GITHUB_CLIENT_ID set for FastAPI application')

GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
if GITHUB_CLIENT_SECRET is None:
    raise ValueError('No GITHUB_CLIENT_SECRET set for FastAPI application')

ACTIVATE_OAUTH2 = os.environ.get('ACTIVATE_OAUTH2')
if ACTIVATE_OAUTH2 is None:
    raise ValueError('No ACTIVATE_OAUTH2 set for FastAPI application')

if ACTIVATE_OAUTH2 == 'True':
    ACTIVATE_OAUTH2 = True
elif ACTIVATE_OAUTH2 == 'False':
    ACTIVATE_OAUTH2 = False
    
ACTIVATE_GITHUB = os.environ.get('ACTIVATE_GITHUB')
if ACTIVATE_GITHUB is None:
    raise ValueError('No ACTIVATE_GITHUB set for FastAPI application')

if ACTIVATE_GITHUB == 'True':
    ACTIVATE_GITHUB = True
elif ACTIVATE_GITHUB == 'False':
    ACTIVATE_GITHUB = False
    
ACTIVATE_GOOGLE = os.environ.get('ACTIVATE_GOOGLE')
if ACTIVATE_GOOGLE is None:
    raise ValueError('No ACTIVATE_GOOGLE set for FastAPI application')

if ACTIVATE_GOOGLE == 'True':
    ACTIVATE_GOOGLE = True
elif ACTIVATE_GOOGLE == 'False':
    ACTIVATE_GOOGLE = False