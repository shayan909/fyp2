import sqlite3
conn = sqlite3.connect('chatbot.db', check_same_thread=False)


# check for indication
def recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness):
    def matchIndication(inputSymptomsOrDiseases):
        IndicationID = []
        DrugIndicationIDs = []
        # Finds Indications matching input in Database
        for i in inputSymptomsOrDiseases:
            cursor = conn.execute('SELECT IndicationID from INDICATION where DISEASE_NAME=?', (i,))
            IndicationID.append(cursor.fetchone())
        IndicationID = [i for i in IndicationID if i]  # Remove None values
        IndicationID = [item for t in IndicationID for item in t]  # Convert to list
        # print("Matched Symptoms/Diseases Indication ID:", IndicationID)
        # Finds Drugs matching Indication in Database
        for i in IndicationID:
            cursor = conn.execute('SELECT DID,IndicationID from INDICATIONS_DRUGS where IndicationID=?', (i,))
            DrugIndicationIDs.append(cursor.fetchall())
        DrugIndicationIDs = [i for i in DrugIndicationIDs if i]  # Remove None values
        DrugIndicationIDs = [item for sublist in DrugIndicationIDs for item in sublist]  # Convert Double List to Single
        return DrugIndicationIDs

    def getDistinctDrugs(DrugIndicationIDs):
        DistinctDrugID = set()
        for i in DrugIndicationIDs:
            DistinctDrugID.add(i[0])
        return DistinctDrugID

    def matchContraindications(DistinctDrugID, CurrentIllness):
        DrugContraindicationID = []
        ContraindicationID = []
        # Finds Contraindications matching input in Database
        for i in CurrentIllness:
            cursor = conn.execute('SELECT ContraindicationID from CONTRAINDICATION where CONDITION_NAME=?', (i,))
            ContraindicationID.append(cursor.fetchone())
        ContraindicationID = [i for i in ContraindicationID if i]  # Remove None Values
        ContraindicationID = [item for t in ContraindicationID for item in t]
        for i in DistinctDrugID:
            for n in ContraindicationID:
                cursor = conn.execute('SELECT DID,ContraindicationID from CONTRAINDICATIONS_DRUGS where DID=? '
                                      'AND ContraindicationID=?', (i, n))
                DrugContraindicationID.append(cursor.fetchone())
        DrugContraindicationID = [i for i in DrugContraindicationID if i]  # Remove None Values
        DrugContraindicationID = set(DrugContraindicationID)
        return DrugContraindicationID

    def matchInteractions(DistinctDrugID, CurrentMedication):
        InteractionID = []
        DrugInteractionID = []
        for i in CurrentMedication:
            cursor = conn.execute('SELECT INTERACTIONS_DRUGS.InteractionID '
                                  'from INTERACTIONS_DRUGS '
                                  'INNER JOIN BRAND ON INTERACTIONS_DRUGS.DID = BRAND.DID '
                                  'WHERE BRAND.NAME=?', (i,))
            InteractionID.append(cursor.fetchone())
        InteractionID = [i for i in InteractionID if i]  # Remove None Values
        InteractionID = [item for t in InteractionID for item in t]
        for i in DistinctDrugID:
            for n in InteractionID:
                cursor = conn.execute('SELECT DID,InteractionID from INTERACTIONS_DRUGS where DID=? '
                                      'AND InteractionID=?', (i, n))
                DrugInteractionID.append(cursor.fetchone())
        DrugInteractionID = [i for i in DrugInteractionID if i]  # Remove None Values
        DrugInteractionID = set(DrugInteractionID)
        return DrugInteractionID

    def getPreferredDrugs(DrugIndicationIDs):
        SeparatedDrugsIndications = set()
        DatabaseDrugs = set()
        DrugIndicationIDsSet = set(DrugIndicationIDs)
        for i in DrugIndicationIDs:
            count = 0
            for n in DrugIndicationIDs:
                if i[1] == n[1]:
                    count = count + 1
                    if count > 1:  # Getting sets of Drugs, Indications that have similar indications
                        SeparatedDrugsIndications.add(i)
                        break
        cursor = conn.execute('SELECT PreferredDrug,ForSymptom from PREFERRED_DRUG_FOR_SYMPTOM')
        DatabaseDrugs = cursor.fetchall()
        DatabaseDrugs = set(DatabaseDrugs)
        PreferredDrugs = SeparatedDrugsIndications.intersection(DatabaseDrugs)
        DrugIndicationIDsSet.difference_update(SeparatedDrugsIndications)
        DrugIndicationIDs = set(DrugIndicationIDs)
        DrugIndicationIDs.difference_update(DrugIndicationIDsSet)
        PreferredDrugs = DrugIndicationIDs.union(PreferredDrugs)
        return PreferredDrugs

    def DiscardDrugs(DrugIndicationIDs, matchedDrugContraindicationID, matchedDrugInteractionID):
        DrugsToBeDeleted = []
        for i in matchedDrugContraindicationID:
            DrugsToBeDeleted.append(i[0])
        for i in matchedDrugInteractionID:
            DrugsToBeDeleted.append(i[0])
        for i in DrugIndicationIDs:
            for n in DrugsToBeDeleted:
                if n in i:
                    DrugIndicationIDs.remove(i)
        return DrugIndicationIDs

    def getDistinctDrugsIndications(PreferredDrugs):
        DistinctDrugIndicationSet = list(PreferredDrugs)
        for i in DistinctDrugIndicationSet:
            count = 0
            for n in DistinctDrugIndicationSet:
                if i[1] == n[1]:
                    count = count + 1
                    if count > 1:
                        DistinctDrugIndicationSet.remove(n)
        return DistinctDrugIndicationSet

    def getRecommendation(DistinctDrugIndicationSet):
        DistinctDrugIndicationSetDict = {}
        theOnesToskip = set()
        for i in DistinctDrugIndicationSet:
            for n in DistinctDrugIndicationSet:
                if i[0] == n[0] and i[0] not in theOnesToskip:
                    DistinctDrugIndicationSetDict.setdefault(i[0], [])
                    DistinctDrugIndicationSetDict[i[0]].append(n[1])
            for x in DistinctDrugIndicationSet:  # Removing all the values that have been worked on
                if x[0] == i[0]:
                    theOnesToskip.add(i)
        print(DistinctDrugIndicationSetDict)
        Drugs = []
        Indications = []
        for key in DistinctDrugIndicationSetDict.keys():
            cursor = conn.execute('SELECT BRAND.name, DRUG.name, ADULT_USAGE.DOSE, ADULT_USAGE.ROUTE, BRAND.FORM, '
                                  'BRAND.MG, BRAND.RETAILPRICE, ADULT_USAGE.INSTRUCTION, DRUG.WARNING '

                                  'FROM DRUG '
                                  'INNER JOIN ADULT_USAGE ON DRUG.DID = ADULT_USAGE.DID '
                                  'INNER JOIN BRAND ON DRUG.DID = BRAND.DID '
                                  'WHERE DRUG.DID=?', (key,))
            Drugs.append(cursor.fetchone())
            for value in DistinctDrugIndicationSetDict.get(key):
                cursor = conn.execute('SELECT DISEASE_NAME FROM INDICATION WHERE IndicationID=?', (value,))
                Indications.append(cursor.fetchone())

        Drugs = [list(ele) for ele in Drugs]  # Convert List of Tuples to lists of List
        for index, drug in enumerate(Drugs):
            temp = [i for i in drug if i]  # Remove None Values
            temp = ' '.join([str(elem) for elem in temp])  # turn List into string
            Drugs[index] = temp
        # tempDrugsList = DistinctDrugIndicationSetDict.keys()
        # allIndicationsForADrug = []
        # for drug in tempDrugsList:
        #     cursor = conn.execute('SELECT INDICATION.DISEASE_NAME '
        #                           'from INDICATIONS_DRUGS '
        #                           'INNER JOIN INDICATION ON INDICATIONS_DRUGS.IndicationID = INDICATION.IndicationID '
        #                           'INNER JOIN DRUG ON INDICATIONS_DRUGS.DID = DRUG.DID '
        #                           'WHERE DRUG.DID=?', (drug,))
        #     allIndicationsForADrug.append(cursor.fetchall())
        Drugs = '\nTake these medications:\n' + '\n'.join([str(elem) for elem in Drugs])  # turn List into string
        return Drugs

    DrugIndicationIDs = matchIndication(inputSymptomsOrDiseases)
    # print("Matched Related Drug ID of Indications with their Indication IDs:", DrugIndicationIDs)

    DistinctDrugID = getDistinctDrugs(DrugIndicationIDs)
    # print("\nDistinct Drugs set:", DistinctDrugID)

    matchedDrugContraindicationID = matchContraindications(DistinctDrugID, inputCurrentIllness)
    # print("\nMatched Related Drugs ID with their Contraindications IDs:", matchedDrugContraindicationID)

    matchedDrugInteractionID = matchInteractions(DistinctDrugID, inputCurrentMedicine)
    # print("\nMatched Related Drugs ID with their InteractionIDs:", matchedDrugInteractionID)

    FilteredDrugsIndications = DiscardDrugs(DrugIndicationIDs, matchedDrugContraindicationID, matchedDrugInteractionID)
    # print("\nDrugs and Indications after minusing Contraindications/Interactions:", FilteredDrugsIndications)

    PreferredDrugs = getPreferredDrugs(FilteredDrugsIndications)
    # print("\nThe Best Drugs after selecting Preferred Drugs:", PreferredDrugs)

    DistinctDrugIndicationSet = getDistinctDrugsIndications(PreferredDrugs)
    # print("\nThe Best Drugs after removing extra Drugs for each Symptom:", DistinctDrugIndicationSet)

    Recommendation = getRecommendation(DistinctDrugIndicationSet)
    # print(Recommendation)

    # for index in range(len(Recommendation)):
    #     Recommendation.insert(index, list(Recommendation[index]))
    # for index, drug in enumerate(Recommendation):
    #     temp = list(drug)
    #     temp = [i for i in temp if i]  # Remove None Values
    #     temp = ' '.join([str(elem) for elem in temp])  # turn List into string
    #     Recommendation.insert(index, temp)
    # Recommendation = 'Take:' + ' '.join([str(elem) for elem in Recommendation])  # turn List into string
    return Recommendation

# things that will be input by user
# inputSymptomsOrDiseases = ['toothache','asthma']
# inputCurrentMedicine = ['panadol']
# inputCurrentIllness = ['diabetes']
# print(recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness))

# things that will be input by user
# inputSymptomsOrDiseases = ['COUGH', 'Wheezing', 'Redness in one or both eyes', 'Itchiness in one or both eyes',
#                            'Watery Eyes', 'Allergy', 'Asthma', 'phlegm', 'Stuffy Nose']
# inputSymptomsOrDiseases = ['COUGH', 'hives', 'Watery Eyes']
# inputCurrentMedicine = []
# inputCurrentIllness = []
# print(recommmendation(inputSymptomsOrDiseases, inputCurrentMedicine, inputCurrentIllness))
