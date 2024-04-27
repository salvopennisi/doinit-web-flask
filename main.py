import logging
from flask import Flask, request
from flask_cors import CORS
from match_people import get_matching_people
from match_groups import get_matching_groups
from dotenv import load_dotenv
import json 

load_dotenv("./.env")

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to DEBUG

app = Flask(__name__)
CORS(app)  # Enable CORS for all endpoints


@app.route("/", methods=["POST"])
def mainPeople():
    try:
        # print(request.json)
        res = request.json
        # logging.debug("Received request data: %s", res)
        people = get_matching_people(res)
        groups = get_matching_groups(res)
        return {"people": json.loads(people), "groups": json.loads(groups)}
    except Exception as e:
        # logging.exception("An error occurred while processing the request: %s", str(e))
        return "An error occurred while processing the request", 500


if __name__ == "__main__":
    # Set the logging level to DEBUG
    app.run(debug=False, host="0.0.0.0", port=8080)
