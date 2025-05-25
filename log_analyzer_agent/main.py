# log_analyzer_agent/main.py
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import os
import json
import random
import threading

app = Flask(__name__)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = os.getenv("PUBSUB_SUB_ID", "log-analysis-test-sub")

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def analyze_message(message):
    data = json.loads(message.data.decode("utf-8"))
    print(f"Received event: {data}")

    # Simulated log analysis
    issue_detected = random.choice([True, False])
    result = {
        "status": "error" if issue_detected else "ok",
        "service": data["service"],
        "summary": "Crash detected" if issue_detected else "All good",
        "commit": data["commit_hash"],
        "timestamp": data["timestamp"]
    }
    print("Analysis Result:", result)
    message.ack()

def pull_loop():
    with subscriber:
        future = subscriber.subscribe(subscription_path, callback=analyze_message)
        try:
            future.result()
        except Exception as e:
            print("Error:", e)
            future.cancel()

@app.route("/", methods=["GET"])
def health():
    return "LogAnalyzerAgent is running", 200

if __name__ == "__main__":
    threading.Thread(target=pull_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
