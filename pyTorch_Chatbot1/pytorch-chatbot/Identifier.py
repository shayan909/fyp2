import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import operator

def fit(features, targetName):
    symptomsOfDataSet = []
    temp = features
    features = {}
    for index, column in enumerate(temp.columns):
        symptomsOfDataSet.append(temp.iat[0, index])
    for index, value in enumerate(symptomsOfDataSet):
        features.update({index:value})
    # Removing None Values from dictionary
    for key, value in dict(features).items():
        if value == 0:
            del features[key]
    return features, targetName


def predict(inputSymptoms, features, targetName):
    temp = inputSymptoms
    inputSymptoms = {}
    temp = [item for sublist in temp for item in sublist]  # convert to List
    for index, value in enumerate(temp):
        inputSymptoms.update({index:value})
    # Removing None Values from dictionary
    for key, value in dict(inputSymptoms).items():
        if value == 0:
            del inputSymptoms[key]
    inputSymptomsKeys = inputSymptoms.keys()
    featuresKeys = features.keys()
    found = set(inputSymptomsKeys).intersection(featuresKeys)
    if found:
        targetName = list(targetName)
        return targetName[0]


def identifierForDisease(inputSymptoms):
    diseases = pd.read_csv("Disease Dataset.csv")
    df = pd.DataFrame(diseases)
    mixedSymptoms = diseases.drop('TARGET', axis='columns')
    target = diseases['TARGET']

    # Converting symptoms to integers
    inputSymptoms = [x.lower() for x in inputSymptoms]
    inputSymptomsIntegers = list(df.columns.drop('TARGET'))
    inputSymptomsIntegers = [x.lower() for x in inputSymptomsIntegers]
    for i in range(len(inputSymptomsIntegers)):
        found = False
        for n in range(len(inputSymptoms)):
            if inputSymptoms[n] == inputSymptomsIntegers[i]:
                inputSymptomsIntegers[i] = 1
                found = True
        if not found:
            inputSymptomsIntegers[i] = 0
    print(inputSymptomsIntegers)

    # Handling Distinct Symptoms
    DiseaseClasses = pd.read_csv("Disease Classes.csv")
    Groups = list(DiseaseClasses['Groups'])
    models = {}
    predictions = []
    for i in Groups:
        if "-" not in i:
            x = i
            dfNew = pd.DataFrame()
            dfNew = dfNew.append(df.loc[(df['TARGET'] == x)])
            target1 = dfNew['TARGET']
            symptoms = dfNew.drop('TARGET', axis='columns')
            features, targetName = fit(symptoms, target1)
            predictions.append(predict([inputSymptomsIntegers], features, targetName))
    print(predictions)
    # Random Forest Classifier
    model = RandomForestClassifier(random_state=0)
    model.fit(mixedSymptoms, target)
    predictionFromModel = model.predict_proba([inputSymptomsIntegers])
    predictionFromModel = [item for sublist in predictionFromModel for item in sublist]  # Convert Double List to Single
    predictionBasedOnProbabilty = {}
    if predictionFromModel:
        for index, Class in enumerate(model.classes_):
            predictionBasedOnProbabilty.update({Class:predictionFromModel[index]})
        print(predictionBasedOnProbabilty)
    # Sort in descending order by value
    predictionDict = dict(sorted(predictionBasedOnProbabilty.items(), key=operator.itemgetter(1), reverse=True))
    count = 0
    predictionFromModel.clear()
    for key in predictionDict.keys():
        count = count +1
        if predictionDict.get(key) >= 0.09 and count < 4:
            predictionFromModel.append(key)
    predictions.extend(predictionFromModel)
    predictions = [i for i in predictions if i]  # Remove None values
    predictions = list(dict.fromkeys(predictions))  # Removing Duplicates
    return predictions