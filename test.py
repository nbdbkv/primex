import requests


body = {
    'phone': '996xxxxxxx',
    'password': 'pass'
}


response  = requests.post('url', body)


print(response.json())
