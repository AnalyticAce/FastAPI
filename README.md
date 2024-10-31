# FastAPIAuth


```bash
SECRET_KEY = "some_hex_string" # generate using "openssl rand -hex 32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MONGO_CONNECTION_STRING="connection_string"
MONGO_DB_NAME="fastapi"
MONGO_COLLECTION_NAME_USER="users"
ACTIVATE_OAUTH2 = "True"
ACTIVATE_GITHUB = "True"
ACTIVATE_GOOGLE = "True"
GITHUB_CLIENT_ID = "github_client_id"
GITHUB_CLIENT_SECRET = "github_client_secret"
```

```bash
sudo docker build -t fastapiapp .
sudo docker-compose up --build -d
```