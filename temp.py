import os
from neo4j import GraphDatabase
import pandas as pd 
import numpy as np
import json 
import logging 




class Neo4jConnection:
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
        

def insert_skill_nodes_from_json(connection, jsonSkill ):
    
    for skill in jsonSkill:
        
        query = f"""
            CREATE (s:{skill['label']})
            set s.name = "{skill['name']}",
                s.category = "{skill['category']}"
            """
        result = connection.run_query(query)
        print('done')
    connection.close()

def insert_business_int_nodes_from_json(connection, businessInterests ):
    
    for interest in businessInterests:
        
        query = f"""
            CREATE (s:Hobbies)
            set s.name = "{interest['name']}",
                s.category = "{interest['category']}"
            """
        result = connection.run_query(query)
        print('done')
    connection.close()
    

file_path = './jsonSkill.json'
file = open(file_path, 'r')
bzsInterst = json.load(file)
file.close()


URI = 'neo4j+ssc://4af74bb1.databases.neo4j.io/:7687' #os.getenv("NEO4J_URI")
AUTH = {"user": os.getenv("NEO4J_USERNAME"), "password": os.getenv("NEO4J_PASSWORD")}
connection = Neo4jConnection(URI, AUTH)
connection.connect()

insert_business_int_nodes_from_json(connection=connection,businessInterests= bzsInterst)
    