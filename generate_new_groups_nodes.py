import faker
import random
import json
from geopy.geocoders import Photon
from neo4j_manager import Neo4jManager
import datetime
import os
from businessInterest_people import businessInterestsObject

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
    return (fake.uuid4()[:20]).replace("-", "")


def generate_random_max_member_numbers():
    maxMembers = random.randint(2, 7)
    return maxMembers

def generate_random_creation_date():
    today = datetime.datetime.today()
    dateDiff = random.randint(0,10)
    date = today - datetime.timedelta(days=dateDiff)
    dateString = datetime.datetime.strftime(date, '%Y-%m-%d')
    return dateString


def choose_members(sectorObjectChoosen, maxMembersNumber):
    experiencedMembers = set(sectorObjectChoosen['ids_interested']) & set(sectorObjectChoosen['ids_experienced'])
    noExperiencedMembers = set(sectorObjectChoosen['ids_interested']) - set(sectorObjectChoosen['ids_experienced'])
    
    membersNumber = random.randint(2, maxMembersNumber)
    experiencedMembersNumber = random.randint(0, membersNumber) if len(experiencedMembers) > membersNumber else random.randint(0, len(experiencedMembers))
    noExperiencedMembersNumber = membersNumber - experiencedMembersNumber
    
    experiencedChosen = random.sample(experiencedMembers, experiencedMembersNumber)
    noExperiencedChosen = random.sample(noExperiencedMembers, noExperiencedMembersNumber)
    
    allMembersChosen = set(experiencedChosen) | set(noExperiencedChosen)
    
    owner = random.choice(list(allMembersChosen))
    allMembersChosen.remove(owner)

    return {'members': list(allMembersChosen), 'owner': owner}


def generate_group():
    try:

        sectorChoosen = random.choice(businessInterestsObject)
        businessSector = sectorChoosen['businessType']
        description = fake.sentence(nb_words=30)
        title =  fake.sentence(nb_words=6)
        id = generate_id()
        city = fake.city()
        position = generate_coordinates(city)
        creationDate = generate_random_creation_date()
        maxParticipants= generate_random_max_member_numbers()
        choosenMembers = choose_members(sectorChoosen,maxParticipants )
        members = choosenMembers['members']
        owner = choosenMembers['owner']

        group = {
            "businessSector": businessSector,
            "description": description,
            "title": title,
            "position": position,
            "creationDate": creationDate,
            "maxParticipants": maxParticipants,
            "id": id,
            'members':members,
            'owner':owner
        }

    except Exception as e:
        print(str(e))
        group = {}

    return group


def create_query():

    group = generate_group()

    businessSector = group["businessSector"]
    description = group["description"]
    position = group["position"]
    title = group["title"]
    id = group["id"]
    creationDate = group['creationDate']
    maxParticipants = group['maxParticipants']
    members = group['members']
    owner = group['owner']


    query = f"""
    CREATE (g:Group {{businessSector: ["{businessSector}"],
                    type:"test",
                    description: "{description}",
                    title: "{title}",
                    creationDate: "{creationDate}",
                    position: point({{longitude:{float(position["longitude"])}, latitude:{float(position["latitude"])}}}),
                    maxParticipants: "{maxParticipants}",
                    id: "{id}"
    }})
    WITH g
    FOREACH (objectName IN {members} |
        MERGE (u:User{{id: objectName}})
        CREATE (u)-[:IS_MEMBER]->(g)
    )
    
    WITH g, "{owner}" AS owner
    MATCH (u:User{{id: owner}})
    CREATE (u)-[:IS_CREATOR]->(g)
    """
    return query


def run_creation_query():
    query = create_query()
    # print(query)
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


main(1000)
connection.close()

