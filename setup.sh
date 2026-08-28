#!/bin/bash
set -e

echo "==> Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    poppler-utils \
    openjdk-17-jre-headless \
    python3-pip

echo "==> Installing Python dependencies..."
pip3 install -r requirements.txt

echo "==> Setup complete!"
