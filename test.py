import requests

def get_access_token():
    body = {
        'phone': '996770266804',
        'password': 'admin'
    }
    response  = requests.post('https://api.domket.kg/account/token/', body)
    token = response.json()['access']
    return token


print(get_access_token())
