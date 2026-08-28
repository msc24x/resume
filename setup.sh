#!/bin/bash
set -e

echo "==> Installing system dependencies..."
sudo sed -i 's/^deb/#deb/' /etc/apt/sources.list.d/strukturag-ubuntu-libressl-jammy.list 2>/dev/null || true
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
