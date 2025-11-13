# RENDER SERVER - Snapchat Chat with Typing + Online + Sound
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# === DATA STORES (Reset on Restart) ===
messages = []  # Chat history
typing_users = {}  # {user: timestamp}
online_users = set()  # Active users
last_seen = {}  # {user: timestamp}

# === CLEANUP THREAD (Remove stale users) ===
def cleanup():
    while True:
        now = time.time()
        expired = [u for u, t in last_seen.items() if now - t > 10]  # 10s inactive
        for u in expired:
            online_users.discard(u)
            typing_users.pop(u, None)
            last_seen.pop(u, None)
        time.sleep(5)

threading.Thread(target=cleanup, daemon=True).start()

# === ROUTES ===
@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.json
        user = data.get('user')
        msg = data.get('msg')
        if user and msg:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({'ts': ts, 'user': user, 'msg': msg})
            last_seen[user] = time.time()
            online_users.add(user)
            typing_users.pop(user, None)  # Stop typing
            return jsonify({'status': 'ok'}), 200
    except:
        pass
    return jsonify({'error': 'bad'}), 400

@app.route('/poll', methods=['GET'])
def poll():
    since = request.args.get('since', 0, type=int)
    user = request.args.get('user', '')
    
    if user:
        last_seen[user] = time.time()
        online_users.add(user)

    # Filter new messages
    new_msgs = [
        m for m in messages
        if int(m['ts'].replace('-','').replace(' ','').replace(':','')) > since
    ]

    # Typing users (not yourself)
    typing = [
        u for u in typing_users
        if u != user and time.time() - typing_users[u] < 3
    ]

    # Online users (not yourself)
    online = list(online_users - {user})

    return jsonify({
        'messages': new_msgs,
        'typing': typing,
        'online': online
    })

@app.route('/typing', methods=['POST'])
def typing():
    try:
        data = request.json
        user = data.get('user')
        if user:
            typing_users[user] = time.time()
            last_seen[user] = time.time()
            online_users.add(user)
            return jsonify({'status': 'ok'}), 200
    except:
        pass
    return jsonify({'error': 'bad'}), 400

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Snapchat Chat LIVE',
        'features': ['typing', 'online', 'sound', 'ephemeral']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
