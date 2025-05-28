from flask import Flask, request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import base64
import json

app = Flask(__name__)

TO_EMAIL = "mynameisyasser123@gmail.com"  # replace with your team email
FROM_EMAIL = "yasser.ibrahim.dev@gmail.com"       # any verified email in SendGrid

@app.route('/', methods=['GET'])
def home():
    
    return "Hello, I am the notifier Agent, 200"

    
  

@app.route('/', methods=['POST'])
def handle_event():
    envelope = request.get_json()
    if not envelope or 'message' not in envelope:
        return 'Bad Request: No message', 400

    pubsub_message = envelope['message']
    data = base64.b64decode(pubsub_message['data']).decode('utf-8')
    event = json.loads(data)

    subject = f"[BUG] {event.get('service')} crash alert"
    body = f"""
    🚨 Bug Detected!
    
    Summary: {event.get('summary')}
    Commit: {event.get('commit')}
    Timestamp: {event.get('timestamp')}
    """

    try:
        send_email(subject, body)
        return 'Notification sent', 200
    except Exception as e:
        print("❌ Failed to send email:", e)
        return 'Error sending email', 500

def send_email(subject, body):
  
    message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject=subject,
    plain_text_content=body)


    print("✅ Key exists:", bool(os.environ.get('SENDGRID_API_KEY')))


    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    sg.send(message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
