from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

db_service_url = "http://db-service:5001/get-transactions-by-address"  # Use internal service name

#example = http://localhost:5000/transactions?address=[bc1qalfaatu5a27qg23srn5vw69a07hdp5dw70ea6jynd7auwzhe2crsepdgwf]
@app.route('/transactions', methods=['GET'])
def transactions():
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address is required'}), 400

    response = requests.get(db_service_url, params={'address': address})
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch transactions'}), 500

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
