import requests

# curl -X POST \
#   http://127.0.0.1:8000/register/ \
#   -H 'Content-Type: application/json' \
#   -d '{
#     "username": "your_username",
#     "email": "your_email@example.com",
#     "password": "your_password"
# }'


username = "Dshalom_"
email = "dossehdosseh14@gmail.com"
password = "123456"

url = "http://127.0.0.1:8000/register/"
data = {
    "username": username,
    "email": email,
    "password": password
}

response = requests.post(url, json=data)
print(response.json())