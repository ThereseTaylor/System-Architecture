#!/bin/bash

# Namespace (if not using default, change this)
NAMESPACE=default

# Delete the services
echo "Deleting Services..."
kubectl delete service gateway-service --namespace=$NAMESPACE
kubectl delete service minio-headless-svc --namespace=$NAMESPACE
kubectl delete service mongodb-headless-svc --namespace=$NAMESPACE
kubectl delete service mongo-express --namespace=$NAMESPACE
kubectl delete service tokenizer-service --namespace=$NAMESPACE
kubectl delete service upload-service --namespace=$NAMESPACE
kubectl delete service rabbitmq --namespace=$NAMESPACE
kubectl delete service ui-service --namespace=$NAMESPACE
kubectl delete service prometheus-service --namespace=$NAMESPACE
kubectl delete service grafana-service --namespace=$NAMESPACE

# Delete the deployments
echo "Deleting Deployments..."
kubectl delete deployment aggregator --namespace=$NAMESPACE
kubectl delete deployment gateway-deployment --namespace=$NAMESPACE
kubectl delete deployment mongo-express --namespace=$NAMESPACE
kubectl delete deployment lexical-richness-micro --namespace=$NAMESPACE
kubectl delete deployment ngram-analysis-micro --namespace=$NAMESPACE
kubectl delete deployment polysyllabic-analysis-micro --namespace=$NAMESPACE
kubectl delete deployment text-cohesion-micro --namespace=$NAMESPACE
kubectl delete deployment tokenizer --namespace=$NAMESPACE
kubectl delete deployment upload-deployment --namespace=$NAMESPACE
kubectl delete deployment user-feedback-deployment --namespace=$NAMESPACE
kubectl delete deployment wordcount --namespace=$NAMESPACE
kubectl delete deployment mongo-save --namespace=$NAMESPACE
kubectl delete deployment ui-deployment --namespace=$NAMESPACE
kubectl delete deployment prometheus-deployment --namespace=$NAMESPACE
kubectl delete deployment grafana-deployment --namespace=$NAMESPACE

# Delete the StatefulSets
echo "Deleting StatefulSets..."
kubectl delete statefulset minio --namespace=$NAMESPACE
kubectl delete statefulset mongodb --namespace=$NAMESPACE
kubectl delete statefulset rabbitmq --namespace=$NAMESPACE

# Delete the DaemonSets

# Delete the ConfigMaps
echo "Deleting ConfigMaps..."
kubectl delete configmap rabbitmq-config --namespace=$NAMESPACE
kubectl delete configmap prometheus-config --namespace=$NAMESPACE
kubectl delete configmap grafana-datasources --namespace=$NAMESPACE

# Delete the ServiceAccounts
echo "Deleting ServiceAccounts..."
kubectl delete serviceaccount rabbitmq --namespace=$NAMESPACE

# Delete the PersistentVolumeClaims
echo "Deleting PersistentVolumeClaims..."
kubectl delete pvc minio-storage-minio-0 --namespace=$NAMESPACE
kubectl delete pvc mongodb-storage-mongodb-0 --namespace=$NAMESPACE
kubectl delete pvc data-rabbitmq-0 --namespace=$NAMESPACE

# Delete the PersistentVolumes


# Delete the StorageClasses
echo "Deleting StorageClasses..."
kubectl delete storageclass minio-dynamic-storage --namespace=$NAMESPACE
kubectl delete storageclass mongodb-dynamic-storage --namespace=$NAMESPACE

# Confirm Deletions
echo "All specified components have been deleted."
