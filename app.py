import logging
from flask import Flask, render_template
import sqlite3
from dotenv import dotenv_values
import requests
import time
import hashlib
import json
from models.character import Character 
from models.comic import Comic

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
config = dotenv_values(".env")

character_name = "Spectrum" # Set the default character name

@app.route("/")
def index():
    # Get character by name (Spectrum)
    character = get_character(character_name)
    if character is None:
        return "No character found"
    # Get character comics
    character.comics = get_character_comics(character.id)
    comics_str = ""
    for comic in character.comics:
        comics_str += str(comic.id) + ","
    # Get related characters from comics (characters that appear in the same comics)
    character.related_characters = get_related_characters(character)
    # save characters and related characters relations in database
    save_related_characters(character)
    return render_template('index.html', character=character)


"""
    This function return the data from the main character
"""
def get_character(name):
    params = get_params()
    url = config['API_URL'] + "/characters?name=" + name
    response = requests.get(url, params=params)
    data = response.json()['data']
    if data['count'] > 0:
        return Character(data['results'][0])
    else:
        return None

"""
    This function return comics from a character
"""
def get_character_comics(character_id):
    params = get_params()
    url = config['API_URL'] + "/characters/" + str(character_id) + "/comics"

    response = requests.get(url, params=params)
    data = response.json()['data']
    total_records = data['total']
    comics = []
    for comic in data['results']:
        comics.append(Comic(comic))
    
    # loop to get all comics by offset and limit set in .env file
    while len(comics) < total_records:
        params['offset'] = len(comics)
        response = requests.get(url, params=params)
        data = response.json()['data']
        for comic in data['results']:
            comics.append(Comic(comic))
    return comics

"""
    This function return the related characters from all main character comics
"""
def get_related_characters(character):
    params = get_params()
    # get get comics ids from character in group of 10
    characters = [] 
    comics_str = "" 
    for comic in character.comics:
        comics_str += str(comic.id) + ","
        if len(comics_str.split(",")) == 11 or comic == character.comics[-1]: # get 10 comics ids at a time
            url = config['API_URL'] + "/characters?comics=" + comics_str
            response = requests.get(url, params=params)
            data = response.json()['data']
            for chara in data['results']:
                if chara['id'] != character.id: # just add characters that are not the main character
                    characters.append(Character(chara))
            comics_str = ""
        
    return remove_duplicate_characters(characters)
    
"""
    This function save the main character and related characters in database
"""
def save_related_characters(character):
    conn = sqlite3.connect(config['DATABASE'])
    c = conn.cursor()

    # select character id if exists
    c.execute("SELECT id FROM characters WHERE id = " + str(character.id))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO characters (id, name, description, picture) \
                    VALUES (?, ?, ?, ?)", (character.id, character.name, character.description, 
                    character.picture))
        conn.commit()
    else:
        c.execute("UPDATE characters SET name = ?,  description = ?, picture = ? \
                    WHERE id = ?", (character.name, character.description, character.picture, 
                    character.id))
        conn.commit()
    # remove existing related characters
    c.execute("DELETE FROM characters_relations WHERE character_one_id = ? OR \
    character_two_id = ?", (character.id, character.id))
    conn.commit()
    for chara in character.related_characters:
        # select character id if exists
        c.execute("SELECT id FROM characters WHERE id = ?", (chara.id,))
        result = c.fetchone()
        if result is None:
            c.execute("INSERT INTO characters (id, name, description, picture) VALUES \
                        (?, ?, ?, ?)", (chara.id, chara.name, chara.description, chara.picture))
            conn.commit()
        else:
            c.execute("UPDATE characters SET name = ?,  description = ?, picture = ? \
                        WHERE id = ?", (chara.name, chara.description, chara.picture, chara.id))
            conn.commit()
        c.execute("INSERT INTO characters_relations (character_one_id, character_two_id) \
                    VALUES (?, ?)", (character.id, chara.id))
        conn.commit()
    conn.close()

"""
    This function remove duplicate characters from a list
"""
def remove_duplicate_characters(characters):
    unique_characters = []
    for character in characters:
        if character.id not in [chara.id for chara in unique_characters]:
            unique_characters.append(character)
    return unique_characters
    
"""
    This function return the params to use in the API request
"""
def get_params():
    ts = str(time.time())
    md5_hash = hashlib.md5(ts.encode() + config['API_PRIVATE_KEY'].encode() 
                + config['API_PUBLIC_KEY'].encode()).hexdigest()
    return {
        "ts": ts, 
        "apikey": config['API_PUBLIC_KEY'], 
        "hash": md5_hash, 
        "limit": config['API_LIMIT']
    }

"""
    This function clean the database data
"""
def clear_database():
    conn = sqlite3.connect(config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM characters")
    c.execute("DELETE FROM characters_relations")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # clean database
    clear_database()
    app.run(host="0.0.0.0", port=80)