# watcher_agent/main.py
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import os
import json

app = Flask(__name__)

# Load environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", "log-analysis-queue")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.route("/", methods=["POST"])
def receive_event():
    data = request.json

    # Example payload for testing
    event = {
        "trigger_type": data.get("type", "push"),
        "timestamp": data.get("timestamp"),
        "service": data.get("service", "api-server"),
        "commit_hash": data.get("commit_hash", "abc123")
    }

    future = publisher.publish(
        topic_path,
        json.dumps(event).encode("utf-8"),
        origin="WatcherAgent"
    )
    return jsonify({"status": "published", "msg_id": future.result()}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
