from flask import Flask, request
from google.cloud import firestore
import base64
import json
import os

app = Flask(__name__)
db = firestore.Client()

@app.route('/', methods=['POST'])
def receive_pubsub():
    envelope = request.get_json()
    if not envelope or 'message' not in envelope:
        return 'Bad Request: No Pub/Sub message received', 400

    pubsub_message = envelope['message']
    data = base64.b64decode(pubsub_message['data']).decode('utf-8')
    event = json.loads(data)

    if event.get("status") == "error":
        report = {
            "service": event.get("service"),
            "summary": event.get("summary"),
            "commit": event.get("commit"),
            "timestamp": event.get("timestamp")
        }
        db.collection("bug_reports").add(report)
        print(f"📄 Bug report stored: {report}")
    else:
        print("✅ No bug found.")

    return 'OK', 200

@app.route('/', methods=['GET'])
def home():
    
    return 'Hello, I am the Bug Reorter Agent', 200

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

