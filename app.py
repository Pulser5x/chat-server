from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
messages = []
online_users = {}  # {name: last_seen_time}

@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.json
        name = data['user']
        msg = data['msg']
        online_users[name] = datetime.now().timestamp()
        if msg.strip():
            messages.append({'ts': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'user': name, 'msg': msg})
        return jsonify({'status': 'ok'})
    except:
        return jsonify({'error': 'bad'}), 400

@app.route('/poll', methods=['GET'])
def poll():
    since = request.args.get('since', '0')
    since_num = int(since.replace('-','').replace(' ','').replace(':',''))
    new_msgs = [m for m in messages if int(m['ts'].replace('-','').replace(' ','').replace(':','')) > since_num]
    
    # Clean old users (offline > 10s)
    now = datetime.now().timestamp()
    online = {k: v for k, v in online_users.items() if now - v < 10}
    online_users.clear()
    online_users.update(online)
    
    return jsonify({
        'messages': new_msgs,
        'online': list(online.keys())
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Snapchat Pro Live'})
