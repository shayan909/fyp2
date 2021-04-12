import random
import json

import torch
from nltk import word_tokenize
from spellchecker import SpellChecker
import symptoms as s_list


from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "MED BOT"


def check(sentence):
    # sentence = input("You: ")
    # if sentence == "quit":
    #     break

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.80:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return intent['responses'][0]
                # print(f"{bot_name}: {random.choice(intent['responses'])}")
    else:
        return "I didn't understand"
        # print(f"{bot_name}: I do not understand...")


# Spell Checking
def spellcorrection(inp):
    myinp = word_tokenize(inp)  # tokenize input
    spell = SpellChecker()  # initialize spellchecker method
    spell.word_frequency.load_text_file("strings.txt")

    misspelled = spell.unknown(myinp)
    mistake = list(misspelled)
    print("mistake")
    print(mistake)

    for i in range(len(mistake)):
        for word in list(spell.candidates(mistake[i])):
            if word in s_list.symptoms:
                inp = inp.replace(mistake[i], word)
            else:
                pass
    print(inp)
    return inp
