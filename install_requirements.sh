#!/bin/bash

# Farben für Terminal-Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting installation of Emotion Detection requirements...${NC}"

# Funktion zum Überprüfen der Installation
check_installed() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 installed successfully${NC}"
    else
        echo -e "${RED}✗ Error installing $1${NC}"
        exit 1
    fi
}

# System-Updates
echo -e "\n${YELLOW}Updating system packages...${NC}"
sudo apt-get update && sudo apt-get upgrade -y
check_installed "System updates"

# System-Dependencies
echo -e "\n${YELLOW}Installing system dependencies...${NC}"
sudo apt-get install -y \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libwebp-dev \
    libtiff5-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgtk-3-dev
check_installed "System dependencies"

# Python virtuelle Umgebung
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python3 -m venv emotion_env
source emotion_env/bin/activate
check_installed "Virtual environment"

# Pip upgrade
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
check_installed "Pip upgrade"

# Requirements installieren
echo -e "\n${YELLOW}Installing Python packages...${NC}"
pip install -r requirements.txt
check_installed "Python packages"

echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "To activate the virtual environment:"
echo -e "source emotion_env/bin/activate"
