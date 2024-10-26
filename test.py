import requests

username = "test"
email = "shalom@gmail.com"
password = "123456"

url = "http://127.0.0.1:8000/register/"
data = {
    "username": username,
    "email": email,
    "password": password
}

response = requests.post(url, json=data)
print(response.json())