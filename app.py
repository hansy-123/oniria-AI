import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")


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
        print("Mode:", mode)
        print("Token received:", token)
        print("Challenge:", challenge)

        # Check token
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

        print("Incoming WhatsApp webhook:")
        print(data)

        return jsonify({
            "status": "success"
        }), 200


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "ONIRIA WhatsApp webhook is running"
    }), 200


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
