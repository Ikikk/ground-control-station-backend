from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return 'Hello, world!'

@app.route('/statemsg', methods=["POST"])
def state_msg():
    id = request.json['id']
    response = {
        'id': id,
        'armed': True,
        'alt': 20.00,
        'mode': "manual",
        'heading':0,
        'vspeed': 32.00,
        'gspeed': 10.00,
        'lat': 60.00,
        'lon': 50.00
    }

    return response

if __name__ == '__main__':
    app.run()
