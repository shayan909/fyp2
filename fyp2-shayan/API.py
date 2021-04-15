from flask import Flask, render_template, request, jsonify
from chat import medical_history, SpellCheck, medicine, critical_symptoms, getOptions, showEntity, removeUnderscore
import spacy

nlp = spacy.load('en_core_sci_lg')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get')
def get_bot_response():
    global count
    global entities
    global symptomSuggestion
    inp = request.args.get('msg')
    if inp:
        inp = inp.lower()
        if len(inp) > 3 and 'count' not in globals():
            correctInp = SpellCheck(inp)
            doc = nlp(inp)

            entities = showEntity(doc, correctInp)

            optionList = getOptions(entities)
            optionList = removeUnderscore(optionList)
            print(entities)
            count = 1
            # call symptom suggestion function
            return jsonify(optionList)

        elif len(inp) > 3 and count == 1:
            # receive suggested symptoms
            symptomSuggestion = inp
            count = 2
            # call critical symptoms function

            return critical_symptoms(inp)

        # elif len(inp) > 3 and count == 2:
        #     # critical symptoms questions

        elif len(inp) > 3 and count == 3:
            count = 4
            return medical_history(inp)

        elif len(inp) > 3 and count == 4:
            return medicine(inp)


if __name__ == "__main__":
    app.run(debug=False)
