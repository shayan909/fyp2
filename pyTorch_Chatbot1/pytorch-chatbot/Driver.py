# from DiseaseClasses import Identification
from MedicineRecommendation import recommmendation
from Identifier import identifierForDisease

def driver(inputCurrentMedicine, inputCurrentIllness, inputSymptoms):
    predictions = []
    inputSymptomsOrDiseases = []  # Symptoms from user + Diseases Identified for Medicine Recommendation
    predictions = identifierForDisease(inputSymptoms)
    predictionString = 'You might be experiencing these problems/diseases: ' + ' '.join(
        [str(elem) for elem in predictions])  # turn list into string
    print(predictionString)
    inputSymptomsOrDiseases.extend(inputSymptoms)
    inputSymptomsOrDiseases.extend(predictions)
    recommmendationString = recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness)
    # print(recommendationString)
    return predictionString, recommmendationString

# inputCurrentMedicine = ['']  # To be taken from chatbot
# inputCurrentIllness = ['']  # To be taken from chatbot
# inputSymptoms = ['fever', 'headache']  # To be taken from chatbot
# predictionDisease, recommmendationDrug = driver(inputCurrentMedicine, inputCurrentIllness, inputSymptoms)
# print(predictionDisease, recommmendationDrug)
