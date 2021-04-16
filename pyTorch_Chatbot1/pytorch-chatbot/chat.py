import json
import pandas as pd
import random

import torch
from nltk import word_tokenize
from spellchecker import SpellChecker
from autocorrect import Speller
import spacy
import symptoms as s_list

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

nlp = spacy.load('en_core_sci_lg')
medModel = spacy.load('en_ner_bc5cdr_md')
medicineModel = spacy.load('en_ner_bionlp13cg_md')
spell = Speller(lang='en')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json') as json_data:
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
    if prob.item() > 0.1:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return intent['tag']
                # print(f"{bot_name}: {random.choice(intent['responses'])}")
    else:
        return "I didn't understand"
        # print(f"{bot_name}: I do not understand...")


# Spell Checking
def SpellCheck(inp):
    myinp = word_tokenize(inp)  # tokenize input
    spelling = SpellChecker()  # initialize spellchecker method
    spelling.word_frequency.load_text_file("strings.txt")

    misspelled = spelling.unknown(myinp)
    mistake = list(misspelled)
    print("mistake")
    print(mistake)

    for i in range(len(mistake)):
        for word in list(spelling.candidates(mistake[i])):
            if word in s_list.symptoms:
                inp = inp.replace(mistake[i], word)
            else:
                inp = inp.replace(mistake[i], spell(mistake[i]))
    print(inp)
    return inp


# Entity Extraction Using SpaCy
def showEntity(inp):
    newLst = []
    inp2 = inp
    doc = nlp(inp)
    if doc.ents:
        for ent in doc.ents:
            if ent.text in s_list.symptoms and ent.text not in newLst:
                newLst.append(ent.text)
                inp2 = inp2.replace(ent.text, " ")
            if check(inp2) not in newLst and check(inp2) in s_list.symptoms:
                print(check(inp2))
                newLst.append(check(inp2))

    return newLst


def medical_history(med):
    medical_details = []
    doc = medModel(med)
    if doc.ents:
        for ent in doc.ents:
            medical_details.append(str(ent.text))
            return str(ent.text)
    # return medical_details[0]


def medicine(med):
    medicine_details = []
    doc = medicineModel(med)
    if doc.ents:
        for ent in doc.ents:
            medicine_details.append(str(ent.text))
            return str(ent.text)


def critical_symptoms(*symptoms):
    criticalSymptoms = ["fever", "cough", "chest discomfort", "chest pain", "wheezing", "sore throat", "headache",
                        "loss of smell", "high fever", "aches"];
    symptoms = list(symptoms)

    for i in range(len(symptoms)):
        if symptoms[i] in criticalSymptoms:
            for intent in intents['intents']:
                if symptoms[i].capitalize() == intent["tag"]:
                    return intent['responses']
                elif symptoms[i].lower() == intent["tag"]:
                    return intent['responses']
                elif (symptoms[i].title()).replace(" ", "_") == intent["tag"]:
                    return intent['responses']


# print(critical_symptoms('fever'))


def getOptions(inputSymptoms):
    extractedCol = set()

    diseases = pd.read_csv("Disease Dataset.csv")
    df = pd.DataFrame(diseases)
    df.columns = df.columns.str.lower()
    #     Processing input Symptoms one by one:
    for inp in inputSymptoms:
        for col_name in df.columns:
            if col_name == inp:
                # Get Rows & Columns where input symptom has value 1
                gp = df[df[inp] == 1][df.columns]
                # print(gp)
                # Get Rows & Columns where column has value 1 in DataFrame 'gp'
                for col in gp.columns:
                    a = gp[col] == 1
                    for b in a:
                        if b:
                            extractedCol.add(col)
                            break
                # print(extractedCol)
                # print(len(extractedCol))

    extractedCol = list(extractedCol ^ set(inputSymptoms))
    if len(extractedCol) > 9:

        return random.sample((extractedCol), 8)
    else:
        return tuple(extractedCol)


# to JSON
def toJSON(extractedCol):
    extractedCol = [x for pair in zip(extractedCol, extractedCol) for x in pair]
    key_list = ["title", "value"]
    # loop to iterate through elements
    # using dictionary comprehension
    # for dictionary construction
    n = len(extractedCol)
    res = []
    for idx in range(0, n, 2):
        res.append({key_list[0]: extractedCol[idx], key_list[1]: extractedCol[idx + 1]})
    return res


# remove underscore
def removeUnderscore(arr):
    for i in range(len(arr)):
        arr[i] = arr[i].replace("_", " ")
    return arr
