from flask import Flask, jsonify
import requests

app = Flask(__name__)

db_service_url = "http://db-service:5001/degree-centrality" 

@app.route('/degree-centrality', methods=['GET'])
def degree_centrality():
    response = requests.get(db_service_url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to calculate degree centrality'}), 500

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
