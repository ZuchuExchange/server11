import os
import logging
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
PAYMENT_URL = os.getenv('PAYMENT_URL', 'https://backend.payhero.co.ke/api/v2/payments')
REFERENCE_STATUS_URL = os.getenv('REFERENCE_STATUS_URL', 'https://backend.payhero.co.ke/api/v2/transaction-status')
AUTH_HEADER = {
    'Authorization': os.getenv('AUTH_HEADER'),
    'Content-Type': 'application/json',
}

@app.route('/pay', methods=['POST'])
def pay():
    try:
        data = request.get_json()
        app.logger.info("Received payment request: %s", data)

        amount = data.get('amount')
        phone_number = data.get('phone_number')

        if not amount or not phone_number:
            return jsonify({'error': 'Missing amount or phone_number'}), 400

        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": 6034,
            "provider": "m-pesa",
            "external_reference": "INV-009",
            "customer_name": "Customer",
            "callback_url": os.getenv('CALLBACK_URL')  # Use env variable
        }

        response = requests.post(PAYMENT_URL, json=payload, headers=AUTH_HEADER)
        response.raise_for_status()
        resp_json = response.json()
        app.logger.info("Payment gateway response: %s", resp_json)

        return jsonify(resp_json)

    except requests.exceptions.HTTPError as e:
        app.logger.error("HTTPError: %s", e)
        return jsonify({'error': str(e), 'response': e.response.text}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error("RequestException: %s", e)
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.exception("Unhandled exception")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/reference_status', methods=['GET'])
def reference_status():
    reference_id = request.args.get('reference')
    if not reference_id:
        return jsonify({'error': 'Missing reference parameter in URL'}), 400
    try:
        url = f"{REFERENCE_STATUS_URL}?reference={reference_id}"
        response = requests.get(url, headers=AUTH_HEADER)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        app.logger.error("HTTPError: %s", e)
        return jsonify({'error': str(e), 'response': e.response.text}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error("RequestException: %s", e)
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.exception("Unhandled exception")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
