import os
import pandas as pd
import numpy as np
import logging
import json
from neo4j_manager import Neo4jManager
from score_calculator import ScoreCalculator

# logging.basicConfig(level=logging.DEBUG)


def get_groups(connection, user_info: dict, max_distance: int = 1000):
    latitude = user_info["position"]["y"]
    longitude = user_info["position"]["x"]
    user_interests = user_info["businessInterests"]
    user_id = user_info["id"]

    query = f"""
        MATCH (u:User)-[r]->(g:Group)
        WHERE u.id <> '{user_id}'
            AND g.businessSector IN {user_interests}
            AND point.distance(g.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 <= {max_distance}
        MATCH (u)-[r1]->(s:Skill)
        MATCH (u)-[r2]->(h:Hobbie)
        OPTIONAL MATCH (u)-[r3:HAS_EXPERIENCE_IN]->(b:BusinessType)
        WITH g,
            point.distance(g.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 <= {max_distance} as straightLineDistance,
            count(DISTINCT u.id) as numberOfmembers,
            collect(DISTINCT s.name) as skill,
            collect(DISTINCT h.name) as hobbies,
            collect(DISTINCT b.name) as experience
        WITH g,
            skill,
            hobbies,
            experience,
            numberOfmembers,
            straightLineDistance,
            apoc.map.setPairs(g,[
                            ['skills',skill]
                            ,['hobbies',hobbies]
                            ,['experience',experience]
                            ,['numberOfmembers',toString(numberOfmembers)]
                            ,['straightLineDistance',straightLineDistance]
                            ]) as group
        WHERE toInteger(group.numberOfmembers) <  toInteger(group.maxParticipants)
        return group

         """
    result = connection.run_query(query)
    connection.close()
    data = [{**item["group"]} for item in result]
    df = pd.DataFrame(data)
    return df


def calculate_exp_score(table_info):
    if table_info["businessSector"] in table_info["experience"]:
        expScore = 10
    else:
        expScore = 0
    return expScore


def calculate_scores(connection, sc, user_info):

    groups = get_groups(connection, user_info=user_info)
    if not groups.empty:
        groups["proximityScore"] = groups.apply(
            lambda row: sc.calculate_proximity_score(
                distance=row["straightLineDistance"]
            ),
            axis=1,
        )
        groups["skillScore"] = groups.apply(
            lambda row: sc.calculate_skills_score(row["skills"], user_info["skills"]),
            axis=1,
        )
        groups["hobbieScore"] = groups.apply(
            lambda row: sc.calculate_hobbies_score(
                row["hobbies"], user_info["hobbies"]
            ),
            axis=1,
        )
        groups["experienceScore"] = groups.apply(
            lambda row: calculate_exp_score(row),
            axis=1,
        )
        groupsWithTotalScore = sc.calculate_total_score(
            df=groups,
            score_columns=[
                "skillScore",
                "proximityScore",
                "hobbieScore",
                "experienceScore",
            ],
        )
        dfSorted = groupsWithTotalScore.sort_values(by="total_score", ascending=False)
        return dfSorted.to_json(orient="records")
    else:
        return {}


def get_matching_groups(user_info):
    URI = "neo4j+ssc://4af74bb1.databases.neo4j.io/:7687"  # os.getenv("NEO4J_URI")
    AUTH = {
        "user": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD"),
    }
    sc = ScoreCalculator(
        max_score_proximity=50, max_score_skills=35, max_score_hobbies=5
    )
    connection = Neo4jManager(URI, AUTH)
    connection.connect()
    data = calculate_scores(connection, sc, user_info)
    return data


# user_info = {
#     "id": "xNgGxgvORo",
#     "position": {"srid": {"low": 4326, "high": 0}, "x": 12.4829321, "y": 41.8933203},
#     "businessInterests": [
#         "Civil Engineering",
#         "Healthcare",
#         "Real Estate Trading",
#         "R&D Partnerships",
#     ],
#     "skills": ["Farming", "Hydroponics"],
#     'hobbies':  ['Photography', 'Cooking', 'Painting', 'Reading']
# }


# with open('groupMatchingTest.json','w') as f:
#     f.write(main(user_info))
