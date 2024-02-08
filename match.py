import dotenv
import os
from neo4j import GraphDatabase
import pandas as pd 
import time
import numpy as np


load_status = dotenv.load_dotenv()
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

class Neo4jConnection:
    def __init__(self, uri, auth):
        self._uri = uri
        self._user = auth["user"]
        self._password = auth["password"]
        self._driver = None

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def connect(self):
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return result.data()




def get_user_by_proximity(distance, user_position, processed_ids):
    # Configura la tua connessione
    URI = os.getenv("NEO4J_URI")
    AUTH = {"user":os.getenv("NEO4J_USERNAME"),"password": os.getenv("NEO4J_PASSWORD")}

    # Crea una connessione
    neo4j_connection = Neo4jConnection(URI, AUTH)
    neo4j_connection.connect()
    latitude =  user_position['latitude']
    longitude = user_position['longitude']
    query = f"""
               MATCH (n:User)
               WHERE point.distance(n.location, point({{latitude: {latitude}, longitude:{longitude}}}))/1000 <= {distance}
               AND NOT n.`_id` IN {processed_ids}
               RETURN n"""
    #print(query)
    result =  neo4j_connection.run_query(query)
    neo4j_connection.close()
    return result


def proximity_score(userInfo, max_distance:int = 10000, increment_distance:int=50,  max_people:int = 4, max_score:int=25, coefficient_score:float=0.15  ):
    
    ids = [userInfo['_id']]
    distance = 0
    people = 0
    valutation = dict()
    while people <= max_people and distance < max_distance  :   
        
        if people == max_people:
            break
        users = get_user_by_proximity(distance, userInfo['location'],ids)

        if len(users) > 0:
            valutation["score_proximity"] =  max_score * (1 - coefficient_score) ** (distance/increment_distance)
        else:
            valutation["score_proximity"] = None

        data = [{**item['n'] , **valutation} for item in users]
        
        [ids.append(item['n']['_id']) for item in users if item['n']['_id'] not in ids]

        if ('df' not in locals() or df.empty):
            df = pd.DataFrame(data)       
        else:
            newDf = pd.DataFrame(data)
            df = pd.concat([df, newDf], ignore_index=True)

        distance = distance + increment_distance
        people =  len(df)
    return df



def get_score(userInfo, threshold_score=70, max_score=25):
    df = proximity_score(userInfo)
    
    for x, y in df.iterrows():
        bz_interest = set(userInfo['Bz_interests']) & set(y['Bz_interests'])
        if len(bz_interest) > 1:
            divisore = max_score * 0.25
            dividendo = (1 + np.exp(-1 * (len(bz_interest) - 1)))
            bz_interest_score = max_score * 0.75 + (divisore / dividendo)
        else:
            bz_interest_score = max_score * 0.75 * len(bz_interest)
        
        df.at[x, "bz_interest_score"] = bz_interest_score

        mergedSkill = set(userInfo['Skills']) & set(y['Skills'])
        sumSkil = set(userInfo['Skills']).union(y['Skills'])
        skills_score = -(max_score / len(sumSkil)) * len(mergedSkill) + max_score
        df.at[x, "skills_score"] = skills_score

        mergedHobbie = set(userInfo['Hobbies']) & set(y['Hobbies'])
        sumHobbies = set(userInfo['Hobbies']).union(y['Hobbies'])
        hobbies_score = (max_score / len(sumHobbies)) * len(mergedHobbie)
        df.at[x, "hobbies_score"] = hobbies_score

        total_score =  y['score_proximity'] + bz_interest_score + skills_score + hobbies_score
        df.at[x, "total_score"] =total_score

    output = df[df["total_score"] >= threshold_score]
    return output.to_json(orient="records")



user = {
          "Nome": "Marco"
        , "Cognome": "Verde"
        , "_id": "8pv9l632qt"
        , "img_profile_link": "https://example.com/marco_profile.jpg"
        , "Citta": "Como"
        , "location": { "longitude":9.149410145408947, "latitude":45.939475900000005}
        ,"Bz_interests": ["Turismo", "E-commerce","Digital Marketing"]
        , "Skills": ["Gestione progetti", "Social Media Marketing"]
        , "Hobbies": ["Escursionismo", "Musica"]      
    }

