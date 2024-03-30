import os
from neo4j import GraphDatabase
import pandas as pd 
import numpy as np
import json 
import logging 

logging.basicConfig(level=logging.DEBUG) 


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

def get_user_by_proximity(connection, user_id:str, user_position:dict, limit:int=100, max_distance:int=1000 ):
    
    latitude = user_position['y']
    longitude = user_position['x']
    
    query = f"""
         MATCH (u:User)
        WHERE point.distance(u.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 <= {max_distance}
        AND  u.id <> '{user_id}'
        WITH u, point.distance(u.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 as straight_line_distance
        OPTIONAL MATCH (u)-[:HAS_SKILLS]->(s:Skills)
        WITH u,straight_line_distance, COLLECT(DISTINCT s.name) AS skills
        OPTIONAL MATCH (u)-[:HAS_BUSINESSINTERESTS]->(b:BusinessInterests)
        WITH u,straight_line_distance, skills, COLLECT(DISTINCT b.name) AS businessInterests
        OPTIONAL MATCH (u)-[:HAS_HOBBIES]->(b:Hobbies)
        WITH u,straight_line_distance, skills, businessInterests, COLLECT(DISTINCT b.name) AS hobbies
        WITH straight_line_distance,businessInterests, hobbies, apoc.map.setKey(properties(u), 'skills', skills) as withSkills
        WITH straight_line_distance,withSkills,hobbies,businessInterests, apoc.map.setKey(withSkills, 'businessInterests', businessInterests) as withBizInterests
        WITH straight_line_distance,withBizInterests, hobbies, apoc.map.setKey(withBizInterests, 'hobbies', hobbies) as withHobbies
        RETURN withHobbies as n, straight_line_distance
            
        ORDER BY straight_line_distance
        {'LIMIT ' + str(limit) if limit is not None else ''}

        """
    print(query)
    result = connection.run_query(query)
    connection.close()
    data = [{ **item["n"], "straight_line_distance": item["straight_line_distance"] } for item in result]
    df = pd.DataFrame(data)
    # print('get_user_prox')
    return df

def calculate_proximity_score(distance, max_score:int=25,coefficient_score:float=0.15,increment_distance:int=50 ):
    return  max_score * (1 - coefficient_score) ** (distance / increment_distance)

def calculate_bz_interest_score(user_businessInterests, table_bz_insterests, max_score:int=35):
    bz_interest = set(table_bz_insterests) & set(user_businessInterests)
    if len(bz_interest) > 1:
        divisor = max_score * 0.25 # per dare piu  importanza a una singola combinazione
        dividend = (1 + np.exp(-1 * (len(bz_interest) - 1)))
        return max_score * 0.75 + (divisor / dividend)
    else:
        return max_score * 0.75 * len(bz_interest)

def calculate_skills_score(user_skills, table_skills, max_score:int=20):
    merged_skill = set(user_skills) & set(table_skills)
    sum_skill = set(user_skills).union(table_skills)
    return -(max_score / len(sum_skill)) * len(merged_skill) + max_score

def calculate_hobbies_score(user_hobbies, table_hobbies, max_score:int=20):
    merged_hobby = set(user_hobbies) & set(table_hobbies)
    sum_hobbies = set(user_hobbies).union(table_hobbies)
    return (max_score / len(sum_hobbies)) * len(merged_hobby)

def calculate_total_score(df):
    df['total_score'] = df['proximity_score']+df['businessInterests_score']+df['skills_score']+df['hobbies_score']
    return df

def get_compatible_features(userInfo, tableInfo, type='inner'):
    compatible_feature = []
    if type=='inner':
        compatible_feature = set(userInfo) & set(tableInfo)   
    elif type =='outer':
        compatible_feature= set(userInfo) - set(tableInfo)  
    return compatible_feature

def get_scores(connection, user_info, threshold_score=20):
    # print('get_scores')
    try:
        matchedUsers = get_user_by_proximity(connection, user_info["id"], user_info["position"])
        matchedUsers['proximity_score'] = matchedUsers['straight_line_distance'].apply(calculate_proximity_score)
        # Utilizza una funzione lambda per passare due parametri
        matchedUsers['businessInterests_score'] = matchedUsers.apply(
            lambda row: calculate_bz_interest_score(row['businessInterests'], user_info['businessInterests']),
            axis=1
        )
        matchedUsers['common_business_interests'] = matchedUsers.apply(
           lambda row: get_compatible_features(row['businessInterests'], user_info['businessInterests']),
            axis=1
        )
        matchedUsers['skills_score'] = matchedUsers.apply(
            lambda row: calculate_skills_score(row['skills'], user_info['skills']),
            axis=1
        )
        matchedUsers['different_skills'] = matchedUsers.apply(
           lambda row: get_compatible_features(row['skills'], user_info['skills'],type='outer'),
            axis=1
        )
        matchedUsers['hobbies_score'] = matchedUsers.apply(
            lambda row: calculate_hobbies_score(row['hobbies'], user_info['hobbies']),
            axis=1
        )
        matchedUsers['common_hobbies'] = matchedUsers.apply(
           lambda row: get_compatible_features(row['hobbies'], user_info['hobbies']),
            axis=1
        )
        scoredMatchedUsers = calculate_total_score(matchedUsers)
        jsonData = scoredMatchedUsers[scoredMatchedUsers["total_score"] >= threshold_score].to_json(orient="records")
        print(jsonData)

        return jsonData
    except Exception as e:
        print(f'errore:\n{e}')
        return []
    finally:
        connection.close()




def get_matching(user_info):
    
    URI = 'neo4j+ssc://4af74bb1.databases.neo4j.io/:7687' #os.getenv("NEO4J_URI")
    print(URI)
    AUTH = {"user": os.getenv("NEO4J_USERNAME"), "password": os.getenv("NEO4J_PASSWORD")}
    connection = Neo4jConnection(URI, AUTH)
    connection.connect()
    data = get_scores(connection, user_info)
    return data





# if __name__ == "__main__":
    
#     os.environ['NEO4J_URI'] = "neo4j+ssc://4af74bb1.databases.neo4j.io"

#     user_info =  {
# 	"id": "xNgGxgvORo",
# 	"firstName": "Salvatore",
# 	"lastName": "Pennisi",
# 	"city": "Roma",
# 	"position": {
# 		"srid": {
# 			"low": 4326,
# 			"high": 0
# 		},
# 		"x": 12.4829321,
# 		"y": 41.8933203
# 	},
# 	"hobbies": [
# 		"Cooking",
# 		"Bodybuilding",
# 		"Reading"
# 	],
# 	"skills": [
# 		"Web Development",
# 		"Software Engineering",
# 		"Catering"
# 	],
# 	"businessInterests": [
# 		"Social Media",
# 		"Web Development",
# 		"Software Development",
# 		"Real Estate"
# 	],
# 	"imgProfileLocation": "https://prflimgs.s3.eu-central-1.amazonaws.com/xNgGxgvORo/1665330192772.jpeg",
# 	"bio": "Gesu di Nazaret"
# }

# env = "C:\\Users\\Salvatore Pennisi\\Desktop\\Git\\MVP Doinit\\doinit-web-flask\\.env"
# load_dotenv(find_dotenv(env))

# print(get_matching(user_info))
