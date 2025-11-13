# FLASK CHAT SERVER - For CodeHS Client (Ryder's Version)
from flask import Flask, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# Simple in-memory "chat room" (messages list)
messages = []  # List of dicts: [{'ts': '...', 'user': 'Ryder', 'msg': 'Hi!'}]

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    if 'user' in data and 'msg' in data:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = {'ts': ts, 'user': data['user'], 'msg': data['msg']}
        messages.append(msg)
        return jsonify({'status': 'sent', 'msg': msg}), 200
    return jsonify({'error': 'Missing user/msg'}), 400

@app.route('/poll', methods=['GET'])
def poll_messages():
    since = request.args.get('since', 0, type=int)  # Timestamp to poll after
    new_msgs = [m for m in messages if int(m['ts'].replace('-', '').replace(' ', '').replace(':', '')) > since]
    return jsonify({'messages': new_msgs})

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Chat server live!', 'url': 'Use /send (POST) and /poll (GET)'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
