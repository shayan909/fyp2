import pandas as pd
import random


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
    print(res)
    return res


def getOptions(inputSymptoms):
    extractedCol = set()

    diseases = pd.read_csv("Disease Dataset.csv")
    df = pd.DataFrame(diseases)
    df.columns = df.columns.str.lower()
    #     Processing input Symptoms one by one:
    for inp in inputSymptoms:
        # inp = inp.capitalize()
        for col_name in df.columns:
            if col_name == inp:
                # Get Rows & Columns where input symptom has value 1
                gp = df[df[inp] == 1][df.columns]
                print(gp)
                # Get Rows & Columns where column has value 1 in DataFrame 'gp'
                for col in gp.columns:
                    a = gp[col] == 1
                    for b in a:
                        if b:
                            extractedCol.add(col)
                            break
                print(extractedCol)
                print(len(extractedCol))
    extractedCol = list(extractedCol)
    if len(extractedCol) > 9:

        return random.sample((extractedCol), 8)
    else:
        return extractedCol


inputSymptoms = ['sore_throat']
symptomsOptions = getOptions(inputSymptoms)
print(symptomsOptions)
toJSON(['sore_throat'])
