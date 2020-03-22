import requests

login = requests.post('http://localhost:8000/login/', {'username': 'admin', 'password': 'admin'})

json = {
    'user': {
        'username': 'luan2'
    },
    "name": "luan"
}

auth_token = 'Bearer ' + login.json()['access']

headers = {'Content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW', 'Authorization': auth_token}

files = {'photo': open('images.jpg', 'r')}

print('sending... ', json)
r = requests.post('http://localhost:8000/user/', files=files, data=json, headers=headers)

print(r.text)
