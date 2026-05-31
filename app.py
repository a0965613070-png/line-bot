from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'LINE BOT 成功運行中！'

@app.route('/callback', methods=['POST'])
def callback():
    return 'OK'

if __name__ == '__main__':
    app.run()
