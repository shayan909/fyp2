from flask import Flask, render_template, request
from chat import check, spellcorrection

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get')
def get_bot_response():
    inp = request.args.get('msg')
    if inp:
        inp = inp.lower()
        input = spellcorrection(inp)
        return check(input)


if __name__ == "__main__":
    app.run(debug=False)
