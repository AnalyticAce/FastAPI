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
