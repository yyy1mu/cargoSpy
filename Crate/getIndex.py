import requests
import pymongo
# https://crates.io/api/v1/crates?page=#{page}&per_page=100

# mongo client
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["index"]
mycol = mydb["package"]

i = 1
url = "https://crates.io/api/v1/crates?page={}&per_page=100".format(i)
package_infos_url = requests.get(url).json()["crates"]

while len(package_infos_url) > 1:
    infos = []
    for info in package_infos_url:
        package_insert_data = {"name": info["id"], "Rust": True}
        infos.append(package_insert_data)
    mycol.insert_many(infos)

    i = i + 1
    url = "https://crates.io/api/v1/crates?page={}&per_page=100".format(i)
    package_infos_url = requests.get(url).json()["crates"]
