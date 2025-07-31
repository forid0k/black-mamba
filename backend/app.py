
---

## 👨‍💻 backend/app.py

```python
import websocket, json, time
from flask import Flask
from flask_socketio import SocketIO
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

candles = []
current_strategy = "ema"
asset = "EURUSD"
tf = "1m"

def generate_signal(candles):
    closes = [c['close'] for c in candles]
    ema = sum(closes[-10:]) / 10
    lst = closes[-1]
    signal = None
    if lst > ema: signal = "BUY"
    elif lst < ema: signal = "SELL"
    return signal

def on_message(ws, msg):
    if msg.startswith("42"):
        try:
            data = json.loads(msg[2:])
            if data[0] == "candle":
                c = data[1].get("candle")
                if c:
                    candles.append(c)
                    if len(candles) > 100: candles.pop(0)
                    sig = generate_signal(candles)
                    if sig:
                        socketio.emit("signal", {
                            "signal": sig,
                            "strategy": current_strategy,
                            "asset": asset,
                            "time": c['time']
                        })
        except Exception as e:
            print("Error:", e)

def on_open(ws):
    time.sleep(1)
    sub = f'42["subscribe", {{"asset":"{asset}","tf":"{tf}"}}]'
    ws.send(sub)

def run_ws():
    ws = websocket.WebSocketApp(
        "wss://ws2.market-qx.trade/socket.io/?EIO=3&transport=websocket",
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()

@app.route("/")
def ping():
    return "OK"

@socketio.on("connect")
def on_connect():
    print("Client connected")

if __name__ == "__main__":
    Thread(target=run_ws, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)
