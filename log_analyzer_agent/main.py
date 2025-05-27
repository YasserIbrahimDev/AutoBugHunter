import os
import json
import base64
import threading
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)
print("🔄Fresh deploy marker")

# Global variables for pull-based subscriber
subscriber = None
subscription_path = None

def initialize_pubsub():
    global subscriber, subscription_path
    project_id = os.getenv("GCP_PROJECT_ID")
    subscription_id = os.getenv("PUBSUB_SUB_ID", "log-analysis-test-sub")

    if not project_id:
        print("❌ GCP_PROJECT_ID is not set")
        return

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    print(f"🔁 Pub/Sub initialized: {subscription_path}")


def analyze_message(message):
    data = json.loads(message.data.decode("utf-8"))
    print(f"✅ Received event (pull): {data}")
    message.ack()

def start_background_listener():
    initialize_pubsub()
    if not subscriber or not subscription_path:
        print("⚠️ Subscriber not initialized.")
        return
    def pull_loop():
        with subscriber:
            future = subscriber.subscribe(subscription_path, callback=analyze_message)
            try:
                future.result()
            except Exception as e:
                print("❌ Error in pull loop:", e)
    thread = threading.Thread(target=pull_loop)
    thread.daemon = True
    thread.start()

@app.route("/", methods=["POST"])
def handle_pubsub_message():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]

    # Decode base64 message
    data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
    print("✅ Received event (push):", json.loads(data))

    return "OK", 200

@app.route("/", methods=["GET"])
def health_check():
    return "Log Analyzer is running", 200

# Start pull listener only when running via Gunicorn in production
if __name__ != "__main__":
    print("🚀 Running in production mode via Gunicorn")
    start_background_listener()
else:
    print("🧪 Running in local development mode")
    if os.getenv("LOCAL_DEV") == "true":
        start_background_listener()
    app.run(debug=True, host="0.0.0.0", port=8080)
