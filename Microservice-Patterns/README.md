# Microservice Architecture Overview

This project was created to implement microservice patterns and interact with a Neo4j Graph Database. The on

The system is a basic microservice-based architecture built to interact with a Neo4j auraDB graph database containing Bitcoin transaction data, structured with transaction nodes connected by input and output edges. Each service runs within its own Docker container. The primary services include:
•	Database Service (DB service): Handles requests to the Neo4j database, receiving two main types of requests:
-	Address Service Requests: The address service sends requests containing a specific user address. The DB service queries the graph database for transactions linked to this address, retrieving relevant transaction nodes and their details.
-	Degree Service Requests: The degree service is focused on analysing transaction connectivity, particularly identifying highly connected transactions. When it sends a request, the DB service queries Neo4j for the top 5 transactions with the highest degree centrality (i.e., transactions with the most connections).
Both services interact with the DB service via an API Gateway. The gateway routes incoming requests from clients, redirecting them to the address service or the degree service accordingly, which then forwards them to the DB service for database interactions. The API Gateway makes use of logging and a simulated Circuit Breaker pattern.

