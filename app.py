from flask import Flask, request
from bot import SparkHook

app = Flask(__name__)


@app.route('/spark', methods=['POST', 'GET'])
def index():
    data = request.get_json()

    if data:
        return SparkHook().handle(data)
    else:
        return 'Ava'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9897, debug=True)
