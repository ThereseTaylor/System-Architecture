from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(user, password))


app = Flask(__name__)

def get_transactions_by_address(address):
    query = """
    MATCH (a:Address {addresses: $address})<-[:INPUT]-(t:Transaction)
    RETURN t.hash AS transaction_hash
    UNION
    MATCH (t:Transaction)-[:OUTPUT]->(a:Address {addresses_1: $address})
    RETURN t.hash AS transaction_hash
    """
    with driver.session() as session:
        result = session.run(query, address=address)
        transactions = [record["transaction_hash"] for record in result]
        return transactions

def calculate_degree_centrality():
    query = """
    MATCH (tx:Transaction)-[r]-()
    RETURN tx.hash AS transactionHash, COUNT(r) AS Degree
    ORDER BY Degree DESC
    LIMIT 5
    """
   
    with driver.session() as session:
        result = session.run(query)
        degrees = [{"transaction": record["transactionHash"], "degree": record["Degree"]} for record in result]
        return degrees

@app.route('/get-transactions-by-address', methods=['GET'])
def transactions():
    address = request.args.get('address')
    transactions = get_transactions_by_address(address)
    return jsonify({'transactions': transactions})

@app.route('/degree-centrality', methods=['GET'])
def degree_centrality():
    centralities = calculate_degree_centrality()
    return jsonify({'centralities': centralities})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)