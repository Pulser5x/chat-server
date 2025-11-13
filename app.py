# app.py
from flask import Flask, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# -------------------------------------------------
# In-memory storage – cleared on every app restart
# -------------------------------------------------
messages = []                     # [{ "ts": "2025-11-12 12:34:56", "user": "...", "msg": "..." }]
online   = {}                     # { user_name: last_seen_timestamp }

# -------------------------------------------------
# Helper: clean old online users
# -------------------------------------------------
def prune_online():
    now = time.time()
    global online
    online = {u: t for u, t in online.items() if now - t < 10}   # 10 s timeout

# -------------------------------------------------
# POST /send
# -------------------------------------------------
@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.get_json(silent=True) or {}
        user = data.get("user", "").strip()
        msg  = data.get("msg", "").strip()

        if not user:
            return jsonify({"error": "missing user"}), 400

        # Update “online” timestamp (heartbeat or real message)
        online[user] = time.time()

        # Store only non-empty messages
        if msg:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({"ts": ts, "user": user, "msg": msg})

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# GET /poll?since=<timestamp>
# -------------------------------------------------
@app.route("/poll", methods=["GET"])
def poll():
    prune_online()
    since = request.args.get("since", "0")
    # Convert the incoming timestamp to an integer (remove - : space)
    try:
        since_int = int(''.join(c for c in since if c.isdigit()))
    except ValueError:
        since_int = 0

    new_msgs = [
        m for m in messages
        if int(''.join(c for c in m["ts"] if c.isdigit())) > since_int
    ]

    return jsonify({
        "messages": new_msgs,
        "online": list(online.keys())
    })

# -------------------------------------------------
# Root – just a health check
# -------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Chat server live – messages reset on restart"})

# -------------------------------------------------
# Run (Render uses `gunicorn` or `python app.py`)
# -------------------------------------------------
if __name__ == "__main__":
    # For local testing only
    app.run(host="0.0.0.0", port=5000, debug=False)
