import requests

url = "https://pypi.org/simple/"
index_url = requests.get(url)

print(index_url)
