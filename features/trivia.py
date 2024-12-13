import json
import random

def get_trivia():
    with open("data/trivia.json", "r") as file:
        trivia = json.load(file)
    question = random.choice(trivia)
    return question["question"], question["answer"]
