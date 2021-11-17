def get_api():
    url = 'https://api.exchangeratesapi.io/v1/symbols?access_key=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzgxOTk0MjEsImlhdCI6MTYzNjkwMzQyMSwic2NvcGUiOiJleGNoYW5nZV9yYXRlIiwicGVybWlzc2lvbiI6MH0.CyAdy2sMnjpKfS28maDDjlCnWrv6b794dKkJIg6tLLM'
    r = requests.get(url)
    r = r.text.encode("UTF8")
    data = json.loads(r)
    file_data = open('data.json', 'wb')
    file_data.write(r)
    file_data.close()

get_api()