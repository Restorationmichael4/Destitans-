import json

def get_quote():
    with open("data/quotes.json", "r") as file:
        quotes = json.load(file)
    return random.choice(quotes)
