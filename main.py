from flask import Flask
from flask_cors import CORS
from match import *

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutti gli endpoint


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

@app.route('/')
def index(userInfo=None):
    group = get_score(user)
    print(group)
    return group

if __name__ == '__main__':
    app.run(debug=True)
