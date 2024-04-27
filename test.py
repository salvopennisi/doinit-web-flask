import requests

def get_random_photo(width, height, category):
    # Endpoint per ottenere una foto casuale da Lorem Picsum con dimensioni personalizzate e categoria specifica
    url = f'https://picsum.photos/{width}/{height}?random&category={category}'

    # Invia una richiesta GET all'API di Lorem Picsum
    response = requests.get(url)

    # Controlla se la richiesta è stata eseguita con successo (codice di stato 200)
    if response.status_code == 200:
        # Estrae l'URL della foto casuale
        photo_url = response.url
        return photo_url
    else:
        # Stampa un messaggio di errore se la richiesta non è stata eseguita con successo
        print(f"Errore: Impossibile recuperare la foto. Codice di stato: {response.status_code}")
        return None

# Specifica le dimensioni desiderate per la foto
width = 600
height = 600

# Specifica la categoria desiderata (ad esempio, "people")
category = "profile"

# Ottieni l'URL della foto casuale con dimensioni personalizzate e categoria specifica
random_photo_url = get_random_photo(width, height, category)

# Stampa l'URL della foto casuale
if random_photo_url:
    print("URL della foto casuale:", random_photo_url)
