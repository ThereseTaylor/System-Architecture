#!/bin/bash

# Remove conflicting Docker-related packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
    sudo apt-get remove -y $pkg
done

# Update package index
sudo apt-get update

# Install necessary dependencies
sudo apt-get install -y ca-certificates curl

# Add Docker's GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index with Docker's repository
sudo apt-get update

# Install Docker packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to the Docker group
sudo usermod -aG docker $USER

# Apply new group membership without logout/login
newgrp docker

echo "Docker installation complete!"

# Install kubectl
echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
if [ $? -eq 0 ]; then
    echo "kubectl installation successful!"
else
    echo "kubectl installation failed."
    exit 1
fi
rm kubectl

# Install Minikube
echo "Installing Minikube..."
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
if [ $? -eq 0 ]; then
    echo "Minikube installation successful!"
else
    echo "Minikube installation failed."
    exit 1
fi
rm minikube-linux-amd64

# Install Helm
echo "Installing Helm..."
sudo snap install helm --classic
if [ $? -eq 0 ]; then
    echo "Helm installation successful!"
else
    echo "Helm installation failed."
    exit 1
fi

# Final message
echo "Docker, kubectl, and Minikube have been successfully installed!"