# FLASK CHAT SERVER - MESSAGES RESET ON RESTART (Snapchat Style)
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# MESSAGES RESET EVERY TIME SERVER RESTARTS
messages = []  # ← Fresh list on every deploy/run

@app.route('/send', methods=['POST'])
def send_message():
    try:
        data = request.json
        if 'user' in data and 'msg' in data:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = {'ts': ts, 'user': data['user'], 'msg': data['msg']}
            messages.append(msg)
            return jsonify({'status': 'sent'}), 200
    except:
        pass
    return jsonify({'error': 'bad request'}), 400

@app.route('/poll', methods=['GET'])
def poll_messages():
    since = request.args.get('since', 0, type=int)
    new_msgs = [m for m in messages 
                if int(m['ts'].replace('-','').replace(' ','').replace(':','')) > since]
    return jsonify({'messages': new_msgs})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'Snapchat-style chat live!',
        'note': 'Messages reset on every server restart!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
