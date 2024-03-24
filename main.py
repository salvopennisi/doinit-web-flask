import logging
from flask import Flask, request
from flask_cors import CORS
from match import get_matching

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to DEBUG

app = Flask(__name__)
CORS(app)  # Enable CORS for all endpoints

@app.route('/', methods=['POST'])
def index():
    try:
        res = request.json
        logging.debug("Received request data: %s", res)
        
        group = get_matching(res)
        return group
    except Exception as e:
        logging.exception("An error occurred while processing the request: %s", str(e))
        return "An error occurred while processing the request", 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
    app.run(debug=True, host='0.0.0.0', port=8080)
