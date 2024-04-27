from neo4j import GraphDatabase

class Neo4jManager:
    def __init__(self, uri, auth, database=None):
        self._uri = uri
        self._user = auth["user"]
        self._password = auth["password"]
        self.database = database
        self._driver = None

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def connect(self):
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password), database=self.database)

    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return result.data()