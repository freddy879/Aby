from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)

# ==========================================
# CORS
# ==========================================

CORS(app)

# ==========================================
# VARIABLES DE ENTORNO
# ==========================================

ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "status": "online",
        "service": "BEBIDASya Zoom API"
    })

# ==========================================
# GENERAR TOKEN
# ==========================================

def get_access_token():

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = (
        "https://zoom.us/oauth/token"
        f"?grant_type=account_credentials"
        f"&account_id={ACCOUNT_ID}"
    )

    response = requests.post(
        url,
        headers=headers
    )

    print("\nTOKEN STATUS:")
    print(response.status_code)

    print("\nTOKEN RESPONSE:")
    print(response.text)

    data = response.json()

    if "access_token" not in data:

        raise Exception(
            f"NO SE PUDO GENERAR TOKEN: {data}"
        )

    return data["access_token"]

# ==========================================
# CREAR REUNION
# ==========================================

@app.route("/create-meeting", methods=["POST"])
def create_meeting():

    try:

        token = get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        meeting_body = {

            "topic": "BEBIDASya Sala",

            "type": 1,

            "settings": {

                "host_video": True,

                "participant_video": True,

                "join_before_host": True,

                "mute_upon_entry": False,

                "waiting_room": False,

                "audio": "both",

                "auto_recording": "none"

            }

        }

        response = requests.post(
            "https://api.zoom.us/v2/users/me/meetings",
            headers=headers,
            json=meeting_body
        )

        print("\nMEETING STATUS:")
        print(response.status_code)

        print("\nMEETING RESPONSE:")
        print(response.text)

        return jsonify(response.json())

    except Exception as e:

        print("\nERROR:")
        print(str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# LISTAR REUNIONES
# ==========================================

@app.route("/meetings")
def meetings():

    try:

        token = get_access_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            "https://api.zoom.us/v2/users/me/meetings",
            headers=headers
        )

        return jsonify(response.json())

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# ELIMINAR REUNION
# ==========================================

@app.route("/delete-meeting/<meeting_id>", methods=["DELETE"])
def delete_meeting(meeting_id):

    try:

        token = get_access_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.delete(
            f"https://://api.zoom.us/v2/meetings/{meeting_id}",
            headers=headers
        )

        if response.status_code == 204:

            return jsonify({
                "success": True,
                "message": "Reunión eliminada"
            })

        return jsonify({
            "success": False,
            "response": response.text
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
