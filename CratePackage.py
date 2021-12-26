class Package:
    def __init__(self, name, version):
        self.name = name
        self.version = version



url = "https://crates.io/api/v1/summary"
import requests
import json

summary = requests.get(url)
if summary.status_code == 200:
    print(summary.json())

