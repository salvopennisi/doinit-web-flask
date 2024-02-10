import dotenv
import os
from neo4j import GraphDatabase
import pandas as pd 
import numpy as np
import json 

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

def get_user_by_proximity(connection, user_id:str, user_position:str, limit:int=100, max_distance:int=1000 ):
    latitude = user_position['latitude']
    longitude = user_position['longitude']
    
    query = f"""
         MATCH (n:User)
        WHERE point.distance(n.location, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 <= {max_distance}
        AND  n._id <> '{user_id}'
        WITH n, point.distance(n.location, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 as straight_line_distance
        RETURN n, straight_line_distance
        ORDER BY straight_line_distance
        {'LIMIT ' + str(limit) if limit is not None else ''}
        """
    result = connection.run_query(query)
    connection.close()
    data = [{ **item["n"], "straight_line_distance": item["straight_line_distance"] } for item in result]
    df = pd.DataFrame(data)
    return df

def calculate_proximity_score(distance, max_score:int=25,coefficient_score:float=0.15,increment_distance:int=50 ):
    return  max_score * (1 - coefficient_score) ** (distance / increment_distance)

def calculate_bz_interest_score(user_bz_interests, table_bz_insterests, max_score:int=25):
    bz_interest = set(table_bz_insterests) & set(user_bz_interests)
    if len(bz_interest) > 1:
        divisor = max_score * 0.25 # per dare piu  importanza a una singola combinazione
        dividend = (1 + np.exp(-1 * (len(bz_interest) - 1)))
        return max_score * 0.75 + (divisor / dividend)
    else:
        return max_score * 0.75 * len(bz_interest)

def calculate_skills_score(user_skills, table_skills, max_score:int=25):
    merged_skill = set(user_skills) & set(table_skills)
    sum_skill = set(user_skills).union(table_skills)
    return -(max_score / len(sum_skill)) * len(merged_skill) + max_score

def calculate_hobbies_score(user_hobbies, table_hobbies, max_score:int=25):
    merged_hobby = set(user_hobbies) & set(table_hobbies)
    sum_hobbies = set(user_hobbies).union(table_hobbies)
    return (max_score / len(sum_hobbies)) * len(merged_hobby)

def calculate_total_score(df):
    df['total_score'] = df['proximity_score']+df['bz_interests_score']+df['skills_score']+df['hobbies_score']
    return df



def get_scores(connection, user_info, threshold_score=70):
    try:
        score_result = get_user_by_proximity(connection, user_info["_id"], user_info["location"])
        score_result['proximity_score'] = score_result['straight_line_distance'].apply(calculate_proximity_score)

        # Utilizza una funzione lambda per passare due parametri
        score_result['bz_interests_score'] = score_result.apply(
            lambda row: calculate_bz_interest_score(row['Bz_interests'], user_info['Bz_interests']),
            axis=1
        )
        score_result['skills_score'] = score_result.apply(
            lambda row: calculate_skills_score(row['Skills'], user_info['Skills']),
            axis=1
        )
        score_result['hobbies_score'] = score_result.apply(
            lambda row: calculate_hobbies_score(row['Hobbies'], user_info['Hobbies']),
            axis=1
        )

        final_data = calculate_total_score(score_result)
        return final_data[final_data["total_score"] >= threshold_score].to_json(orient="records")
    except Exception as e:
        print(e)
    finally:
        connection.close()




def get_matching(user_info):
    dotenv.load_dotenv()
    URI = os.getenv("NEO4J_URI")
    AUTH = {"user": os.getenv("NEO4J_USERNAME"), "password": os.getenv("NEO4J_PASSWORD")}
    connection = Neo4jConnection(URI, AUTH)
    connection.connect()
    data = get_scores(connection, user_info)
    return data





if __name__ == "__main__":
    
    user_info =  {
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
    
    print(get_matching(user_info))
