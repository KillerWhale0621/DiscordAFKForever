from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "機器人正在運行中！"

def run():
    # 綁定 0.0.0.0 讓外部可以訪問，Port 預設使用 8080
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()