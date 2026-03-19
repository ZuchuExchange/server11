import os
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Payment gateway details
PAYMENT_URL = 'https://backend.payhero.co.ke/api/v2/payments'
REFERENCE_STATUS_URL = 'https://backend.payhero.co.ke/api/v2/transaction-status'
AUTH_HEADER = {
    'Authorization': 'Basic RVJKbWpSTDRYbTUyUlVLWVpEN3k6eHFYV3ZwdkZTVlpYVm9yYmMyTUxoZWJJOE50OTFxTFg3WDhjcXlKOQ== ',
    'Content-Type': 'application/json',
}

@app.route('/pay', methods=['POST'])
def pay():
    try:
        data = request.get_json()
        print("Received payment request:", data)

        amount = data.get('amount')
        phone_number = data.get('phone_number')

        if not amount or not phone_number:
            return jsonify({'error': 'Missing amount or phone_number'}), 400

        # Prepare payload for payment gateway
        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": 6034,
            "provider": "m-pesa",
            "external_reference": "INV-009",
            "customer_name": "Customer",
            "callback_url": "https://196.96.187.69:5000/callback"  # Replace with your actual URL
        }

        response = requests.post(PAYMENT_URL, json=payload, headers=AUTH_HEADER)
        response.raise_for_status()
        resp_json = response.json()
        print("Payment gateway response:", resp_json)

        return jsonify(resp_json)

    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e)
        return jsonify({
            'error': str(e),
            'response': e.response.text
        }), 500
    except requests.exceptions.RequestException as e:
        print("RequestException:", e)
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print("Unhandled exception:", e)
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/reference_status', methods=['GET'])
def reference_status():
    reference_id = request.args.get('reference')
    if not reference_id:
        return jsonify({'error': 'Missing reference parameter in URL'}), 400
    try:
        # Build the URL with the reference_id
        url = f"{REFERENCE_STATUS_URL}?reference={reference_id}"
        response = requests.get(url, headers=AUTH_HEADER)
        response.raise_for_status()
        # Return the response directly
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e)
        return jsonify({
            'error': str(e),
            'response': e.response.text
        }), 500
    except requests.exceptions.RequestException as e:
        print("RequestException:", e)
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print("Unhandled exception:", e)
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Run Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)