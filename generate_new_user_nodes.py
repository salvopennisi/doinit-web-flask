import faker
import random
from geopy.geocoders import Photon
from neo4j_manager import Neo4jManager
import os
from categories import allBusinessInterests, allHobbies, allSkills, photoUrls

URI = "neo4j+ssc://4af74bb1.databases.neo4j.io/:7687"  # os.getenv("NEO4J_URI")
AUTH = {
    "user": os.getenv("NEO4J_USERNAME"),
    "password": os.getenv("NEO4J_PASSWORD"),
}
connection = Neo4jManager(URI, AUTH)
connection.connect()
geolocator = Photon()
fake = faker.Faker("it_IT")



def generate_coordinates(city):

    location = geolocator.geocode(city)
    return {"longitude": location.longitude, "latitude": location.latitude}


# Funzione per generare un ID casuale di lunghezza 10
def generate_id():
    return (fake.uuid4()[:10]).replace("-", "")


def generate_random_features(container, min_random_edge=5, max_random_edge=15):
    num_elements = random.randint(min_random_edge, max_random_edge)
    features = random.choices(container, k=num_elements)
    return features

def get_random_photos():
    photo = random.choice(photoUrls)
    return photo

def get_random_business_experience(businessInterestsChoosen):
    experienceChoice = random.randint(0,2)
    if experienceChoice == 1:
        businessExperienceChoosen = generate_random_features(allBusinessInterests, min_random_edge=1, max_random_edge=5) 
    elif experienceChoice == 0:
        businessExperienceChoosen = generate_random_features(businessInterestsChoosen, min_random_edge=1, max_random_edge=3) 
    else:
        businessExperienceChoosen = []
    return businessExperienceChoosen


def generate_user():
    try:

        first_name = fake.first_name()
        last_name = fake.last_name()
        id = generate_id()
        imgProfileLocation = get_random_photos()
        city = fake.city()
        position = generate_coordinates(city)
        bio = fake.sentence()
        skillsChoosen = generate_random_features(allSkills)
        hobbiesChoosen = generate_random_features(allHobbies)
        businessInterestsChoosen = generate_random_features(allBusinessInterests)
        businessExperienceChoosen = get_random_business_experience(businessInterestsChoosen)

        user = {
            "firstName": first_name,
            "type": "test",
            "lastName": last_name,
            "city": city,
            "position": position,
            "imgProfileLocation": imgProfileLocation,
            "bio": bio,
            "id": id,
            'skills': skillsChoosen,
            'hobbies': hobbiesChoosen,
            'businessInterests': businessInterestsChoosen,
            'businessExperience': businessExperienceChoosen
        }

    except Exception as e:
        print(str(e))
        user = {}

    return user


def create_query():

    user = generate_user()

    firstName = user["firstName"]
    lastName = user["lastName"]
    city = user["city"]
    position = user["position"]
    bio = user["bio"]
    id = user["id"]
    imgProfileLocation = user['imgProfileLocation']
    skillsChoosen = user['skills']
    hobbiesChoosen = user['hobbies']
    businessInterestsChoosen = user['businessInterests']
    businessExperienceChoosen = user['businessExperience']

    query = f"""
    CREATE (u:User {{firstName: "{firstName}",
                    type:"test",
                    lastName: "{lastName}",
                    imgProfileLocation: "{imgProfileLocation}",
                    city: "{city}",
                    position: point({{longitude:{float(position["longitude"])}, latitude:{float(position["latitude"])}}}),
                    bio: "{bio}",
                    id: "{id}"
    }})
    WITH u
    FOREACH (objectName IN {skillsChoosen} |
        MERGE (s:Skill{{name: objectName}})
        CREATE (u)-[:IS_SKILLED_IN]->(s)
    )
    FOREACH (objectName IN {hobbiesChoosen} |
        MERGE (h:Hobbie{{name: objectName}})
        CREATE (u)-[:IS_PASSIONATE_ABOUT]->(h)
    )
    FOREACH (objectName IN {businessInterestsChoosen} |
        MERGE (b:BusinessType{{name: objectName}})
        CREATE (u)-[:IS_INTERESTED_IN]->(b)
    )
    FOREACH (objectName IN  {businessExperienceChoosen} |
        MERGE (b:BusinessType{{name: objectName}})
        CREATE (u)-[:HAS_EXPERIENCE_IN]->(b)
    )
    """
    return query


def run_creation_query():
    query = create_query()
    connection.run_query(query)


def main(numbers_of_iterations):
    for number in range(0, numbers_of_iterations):
        percent = (100 *number)/numbers_of_iterations
        if percent%5 == 0:
            print(f'caricamento nodi al {percent} %...')
        try:
            run_creation_query()
        except Exception as e:
            print(f"Qualcosa è andato storto:\n{str(e)}")
        finally:
            connection.close()


main(2000)
connection.close()

