import os
import pandas as pd
import numpy as np
import logging
from neo4j_manager import Neo4jManager
from score_calculator import ScoreCalculator

# logging.basicConfig(level=logging.DEBUG)


def get_user_by_proximity(
    connection,
    user_id: str,
    user_position: dict,
    limit: int = 100,
    max_distance: int = 1000,
):

    latitude = user_position["y"]
    longitude = user_position["x"]

    query = f"""
         MATCH (u:User)
        WHERE point.distance(u.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 <= {max_distance}
        AND  u.id <> '{user_id}'
        WITH u, point.distance(u.position, point({{latitude: {latitude}, longitude: {longitude}}}))/1000 as straight_line_distance
        OPTIONAL MATCH (u)-[:IS_SKILLED_IN]->(s:Skill)
        WITH u,straight_line_distance, COLLECT(DISTINCT s.name) AS skills
        OPTIONAL MATCH (u)-[:IS_INTERESTED_IN]->(b:BusinessType)
        WITH u,straight_line_distance, skills, COLLECT(DISTINCT b.name) AS businessInterests
        OPTIONAL MATCH (u)-[:IS_PASSIONATE_ABOUT]->(b:Hobbie)
        WITH u,straight_line_distance, skills, businessInterests, COLLECT(DISTINCT b.name) AS hobbies
        OPTIONAL MATCH (u)-[:HAS_EXPERIENCE_IN]->(e:BusinessType)
        WITH u,straight_line_distance, skills, businessInterests, hobbies, COLLECT( DISTINCT e.name) as businessExperience
        WITH straight_line_distance,businessExperience,skills,businessInterests, hobbies, apoc.map.setKey(properties(u), 'skills', skills) as withSkills
        WITH straight_line_distance,businessExperience,withSkills,hobbies,businessInterests, apoc.map.setKey(withSkills, 'businessInterests', businessInterests) as withBizInterests
        WITH straight_line_distance,businessExperience,withBizInterests, hobbies, apoc.map.setKey(withBizInterests, 'hobbies', hobbies) as withHobbies
        WITH straight_line_distance,businessExperience,withHobbies, apoc.map.setKey(withHobbies, 'businessExperience', businessExperience) as withBusinessExperience
        RETURN withBusinessExperience as n, straight_line_distance
        ORDER BY straight_line_distance
        {'LIMIT ' + str(limit) if limit is not None else ''}

        """
    result = connection.run_query(query)
    connection.close()
    data = [
        {**item["n"], "straight_line_distance": item["straight_line_distance"]}
        for item in result
    ]
    df = pd.DataFrame(data)
    # print('get_user_prox')
    return df


def get_compatible_features(userInfo, tableInfo, type="inner"):
    compatible_feature = []
    if type == "inner":
        compatible_feature = set(userInfo) & set(tableInfo)
    elif type == "outer":
        compatible_feature = set(userInfo) - set(tableInfo)
    return compatible_feature


def get_scores(connection, sc, user_info, threshold_score=50):
    # print('get_scores')
    try:
        matchedUsers = get_user_by_proximity(
            connection, user_info["id"], user_info["position"]
        )
        matchedUsers["proximity_score"] = matchedUsers.apply(
            lambda row: sc.calculate_proximity_score(
                distance=row["straight_line_distance"]
            ),
            axis=1,
        )
        # Utilizza una funzione lambda per passare due parametri
        matchedUsers["businessInterests_score"] = matchedUsers.apply(
            lambda row: sc.calculate_bz_interest_score(
                row["businessInterests"], user_info["businessInterests"]
            ),
            axis=1,
        )
        matchedUsers["common_business_interests"] = matchedUsers.apply(
            lambda row: get_compatible_features(
                row["businessInterests"], user_info["businessInterests"]
            ),
            axis=1,
        )
        matchedUsers["businessExperience_score"] = matchedUsers.apply(
            lambda row: sc.calculate_bz_exp_score(
                user_businessInterests=user_info["businessInterests"],
                table_business_exp=row["businessExperience"],
                table_bz_insterests=row["businessInterests"],
            ),
            axis=1,
        )

        matchedUsers["skills_score"] = matchedUsers.apply(
            lambda row: sc.calculate_skills_score(row["skills"], user_info["skills"]),
            axis=1,
        )
        matchedUsers["different_skills"] = matchedUsers.apply(
            lambda row: get_compatible_features(
                row["skills"], user_info["skills"], type="outer"
            ),
            axis=1,
        )
        matchedUsers["hobbies_score"] = matchedUsers.apply(
            lambda row: sc.calculate_hobbies_score(
                row["hobbies"], user_info["hobbies"]
            ),
            axis=1,
        )
        matchedUsers["common_hobbies"] = matchedUsers.apply(
            lambda row: get_compatible_features(row["hobbies"], user_info["hobbies"]),
            axis=1,
        )
        scoredMatchedUsers = sc.calculate_total_score(
            df=matchedUsers,
            score_columns=[
                "hobbies_score",
                "skills_score",
                "businessInterests_score",
                "proximity_score",
                "businessExperience_score",
            ],
        )
        jsonData = scoredMatchedUsers[
            scoredMatchedUsers["total_score"] >= threshold_score
        ].to_json(orient="records")

        return jsonData
    except Exception as e:
        print(f"errore:\n{e}")
        return []
    finally:
        connection.close()


def get_matching_people(user_info):

    URI = "neo4j+ssc://4af74bb1.databases.neo4j.io/:7687"  # os.getenv("NEO4J_URI")
    AUTH = {
        "user": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD"),
    }
    connection = Neo4jManager(URI, AUTH)
    connection.connect()
    sc = ScoreCalculator()
    data = get_scores(connection, sc, user_info)
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

# with open('matchPeople.json', 'w') as f:
#     match = get_matching(user_info)
#     f.write(match)
