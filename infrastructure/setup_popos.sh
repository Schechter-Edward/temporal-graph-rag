#!/bin/bash
set -e

echo "Setting up Temporal Graph RAG on Pop!_OS"

if ! grep -q "Pop!_OS" /etc/os-release; then
  echo "Warning: this script is optimized for Pop!_OS"
fi

sudo apt update
sudo apt install -y docker.io docker-compose-plugin python3.11 python3.11-venv python3.11-pip

sudo usermod -aG docker "$USER"

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. Log out/in to refresh docker group."
