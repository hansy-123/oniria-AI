import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

# ============================================================
# HELPER FUNCTION: SEND WHATSAPP MESSAGE
# ============================================================
def send_whatsapp_message(to_number, text_content):
    """Sends a standard text message using the Meta Cloud API."""
    if not WHATSAPP_ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("ERROR: Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID in environment variables.")
        return False

    url = f"https://facebook.com{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text_content
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Sent message to {to_number}. Status Code: {response.status_code}")
        print("Meta API Response:", response.json())
        return response.status_code == 200
    except Exception as e:
        print("Exception occurred while sending message:", str(e))
        return False

# ============================================================
# WEBHOOK
# ============================================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # --------------------------------------------------------
    # META / WHATSAPP WEBHOOK VERIFICATION
    # --------------------------------------------------------
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        print("Webhook verification request received")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verification successful")
            return challenge, 200

        print("Webhook verification failed")
        return "Verification failed", 403

    # --------------------------------------------------------
    # WHATSAPP INCOMING WEBHOOK EVENTS
    # --------------------------------------------------------
    if request.method == "POST":
        data = request.get_json(silent=True)
        print("Incoming WhatsApp webhook payload:", data)

        # Parse message structure safely to extract sender and text content
        try:
            if data and "entry" in data and data["entry"][0]["changes"][0]["value"].get("messages"):
                message_details = data["entry"][0]["changes"][0]["value"]["messages"][0]
                
                # Get the user's phone number and message body
                sender_phone = message_details["from"]
                
                # Check if it is a text message
                if message_details.get("type") == "text":
                    incoming_text = message_details["text"]["body"]
                    print(f"Received text '{incoming_text}' from {sender_phone}")

                    # --------------------------------------------------------
                    # CHATBOT REPLY LOGIC
                    # --------------------------------------------------------
                    reply_text = f"Hello! You sent: '{incoming_text}'. This is an automated response from your ONIRIA bot."
                    send_whatsapp_message(sender_phone, reply_text)

        except Exception as parse_error:
            print("Error parsing incoming webhook structure:", str(parse_error))

        return jsonify({"status": "success"}), 200

# ============================================================
# HOME / HEALTH CHECK
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "ONIRIA WhatsApp webhook is running smoothly"
    }), 200

# ============================================================
# START SERVER
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
