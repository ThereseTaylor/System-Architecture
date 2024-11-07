# Microservice Architecture Overview

## address-service
**Technology Stack**: Flask, Python

**Description**: This service is likely a REST API built with Flask. It may handle HTTP requests for specific functionalities such as user management, data processing, or serving as a gateway to other services.

**Overview**:
apiVersion: apps/v1
kind: Deployment
metadata:
name: address-deployment
labels:

---

## db-service
**Technology Stack**: Flask, Python

**Description**: This service is likely a REST API built with Flask. It may handle HTTP requests for specific functionalities such as user management, data processing, or serving as a gateway to other services.

**Overview**:
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import os
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")

---

## degree-service
**Technology Stack**: Flask, Python

**Description**: This service is likely a REST API built with Flask. It may handle HTTP requests for specific functionalities such as user management, data processing, or serving as a gateway to other services.

**Overview**:
apiVersion: apps/v1
kind: Deployment
metadata:
name: degree-deployment
labels:

---

## gateway-service
**Technology Stack**: Flask, Python

**Description**: This service is likely a REST API built with Flask. It may handle HTTP requests for specific functionalities such as user management, data processing, or serving as a gateway to other services.

**Overview**:
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app

---

