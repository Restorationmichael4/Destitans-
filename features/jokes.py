import json

def get_joke():
    with open("data/jokes.json", "r") as file:
        jokes = json.load(file)
    return random.choice(jokes)
