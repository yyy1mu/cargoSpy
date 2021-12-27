import requests
from neo4j import GraphDatabase
import pymongo


class Neo4jDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]

    def execute(self, message):
        with self.driver.session() as session:
            if "Python" not in message:
                session.write_transaction(self._add_package, message["name"], message["Rust"])
            else:
                session.write_transaction(self._add_package, message["name"], message["Rust"], message["Python"])

    def relation(self, package, deps):
        with self.driver.session() as session:
            for dependent in deps:
                session.write_transaction(self._add_relation, package, dependent)

    @staticmethod
    def _add_relation(tx, package, dependent):
        CQL = "MATCH (a:package{name:\"" + package + "\"}),(b:package{name:\"" + dependent + "\"}) MERGE (a)-[r:dependent]->(b) RETURN r"
        tx.run(CQL)

    @staticmethod
    def _add_package(tx, name, cargo=False, pypi=False):
        tx.run("MERGE (a:package {name: $name, cargo: $cargo, pypi: $pypi}) ",
               name=name, cargo=cargo, pypi=pypi)


def lastest_version(name):
    url = "https://crates.io/api/v1/crates/{}".format(name)
    return requests.get(url).json()["versions"][0]["num"]


def dependencies(name, version):
    url = "https://crates.io/api/v1/crates/{0}/{1}/dependencies".format(name, version)
    res = requests.get(url).json()["dependencies"]
    deps = [q["crate_id"] for q in res]
    return deps


if __name__ == "__main__":
    package_db = Neo4jDB("bolt://localhost:7687", "neo4j", "777888")

    # mongo client
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["index"]
    mycol = mydb["package"]
    cus = mycol.find({}).batch_size(100)
    while cus.alive:

        for item in cus:
            name = item["name"]
            print(name)
            version = lastest_version(name)
            deps = dependencies(name, version)
            package_db.relation(name, deps)

        cus = cus.next()

    # greeter.print_greeting("hello, world")
    package_db.close()
