import logging
import os
from flask import Flask, jsonify, request
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
import time

app = Flask(__name__)

# Configure root logger
log_file_path = "/logs/gateway.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),   # Log to file
        logging.StreamHandler()               # Log to console
    ]
)

logger = logging.getLogger()  # Use the root logger directly

# Test log entry to confirm setup
logger.info("Root logger is set up and logging to both file and console.")

# Define service URLs
degree_centrality_service_url = "http://degree-service:5002/degree-centrality"
transactions_service_url = "http://address-service:5000/transactions"

# Circuit breaker state variables
failure_threshold = 3
cool_off_period = 10
failure_count = 0
last_failure_time = None

# Log requests
@app.before_request
def log_request():
    logger.info(f"Received {request.method} request on {request.path} with args: {request.args}")

# Log responses
@app.after_request
def log_response(response):
    logger.info(f"Responding with status {response.status_code} for {request.path}")
    return response

# Retry decorator simulating a circuit breaker
@retry(stop=stop_after_attempt(failure_threshold), wait=wait_fixed(1))
def make_request(url, params=None):
    global failure_count, last_failure_time
    
    # Check if in cool-off period
    if failure_count >= failure_threshold:
        if last_failure_time and (time.time() - last_failure_time < cool_off_period):
            raise Exception("Circuit breaker is open - service is in cool-off period.")
        else:
            # Reset circuit breaker after cool-off period
            failure_count = 0
            last_failure_time = None
    
    # Make the request
    response = requests.get(url, params=params)
    
    # Check if the request failed
    if response.status_code != 200:
        failure_count += 1
        last_failure_time = time.time()
        raise Exception(f"Failed request with status code {response.status_code}")
    
    # Reset failure count if successful
    failure_count = 0
    return response

# Gateway route to access degree centrality
@app.route('/api/degree-centrality', methods=['GET'])
def gateway_degree_centrality():
    try:
        response = make_request(degree_centrality_service_url)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Circuit breaker open or other error occurred: {e}")
        return jsonify({'error': 'Service temporarily unavailable'}), 503

# Gateway route to access transactions by address
@app.route('/api/transactions', methods=['GET'])
def gateway_transactions():
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address is required'}), 400

    try:
        response = make_request(transactions_service_url, params={'address': address})
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Circuit breaker open or other error occurred: {e}")
        return jsonify({'error': 'Service temporarily unavailable'}), 503

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
