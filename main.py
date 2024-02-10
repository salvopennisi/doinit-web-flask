from flask import Flask
from flask import request
from flask_cors import CORS
from match import get_matching

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutti gli endpoint



@app.route('/', methods=['POST'])
def index():
    res = request.json
    print(res)
    group = get_matching(res)
    return group

if __name__ == '__main__':
    app.run(debug=True)
