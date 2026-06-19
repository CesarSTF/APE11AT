from flask import Flask, request, jsonify, render_template
from parcer import parser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    eq1 = data.get('eq1', '').strip()
    eq2 = data.get('eq2', '').strip()

    if not eq1 or not eq2:
        return jsonify({"status": "error", "msg": "Debe ingresar ambas ecuaciones."})

    input_text = f"{eq1}\n{eq2}"

    try:
        result = parser.parse(input_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
