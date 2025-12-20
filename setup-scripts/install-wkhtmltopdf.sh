#!/bin/bash
# GCP VM Odoo wkhtmltopdf Installation with libssl1.1 Fix (Updated 2025)
# Works on Ubuntu 20.04, 22.04, 24.04

set -e

echo "=== Installing Patched wkhtmltopdf on GCP VM ==="

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Detect Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
echo "Detected Ubuntu version: $UBUNTU_VERSION"

# Add focal-security repository for libssl1.1 compatibility
echo "Setting up libssl1.1 compatibility..."
echo "deb http://security.ubuntu.com/ubuntu focal-security main" | sudo tee /etc/apt/sources.list.d/focal-security.list > /dev/null
sudo apt-get update
sudo apt-get install -y libssl1.1

# Install all required dependencies
echo "Installing dependencies..."
sudo apt-get install -y \
    fontconfig \
    fontconfig-config \
    fonts-dejavu-core \
    fonts-liberation \
    libfontenc1 \
    libfreetype6 \
    libjpeg-turbo-progs \
    libjpeg8 \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-encodings \
    xfonts-utils \
    wget \
    curl

# Download patched wkhtmltopdf based on version
cd /tmp

if [ "$UBUNTU_VERSION" = "24.04" ]; then
    echo "Installing for Ubuntu 24.04..."
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.noble_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.6.1-2.noble_amd64.deb || sudo apt-get install -yf
    rm -f wkhtmltox_0.12.6.1-2.noble_amd64.deb
elif [ "$UBUNTU_VERSION" = "22.04" ]; then
    echo "Installing for Ubuntu 22.04..."
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb || sudo apt-get install -yf
    rm -f wkhtmltox_0.12.6.1-2.jammy_amd64.deb
elif [ "$UBUNTU_VERSION" = "20.04" ]; then
    echo "Installing for Ubuntu 20.04..."
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.focal_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.6.1-2.focal_amd64.deb || sudo apt-get install -yf
    rm -f wkhtmltox_0.12.6.1-2.focal_amd64.deb
else
    echo "Ubuntu $UBUNTU_VERSION detected. Attempting Jammy version (Ubuntu 22.04 compatible)..."
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb || sudo apt-get install -yf
    rm -f wkhtmltox_0.12.6.1-2.jammy_amd64.deb
fi

# Fix any remaining dependencies
echo "Fixing any remaining dependencies..."
sudo apt-get install -yf

# Verify installation
echo "Verifying installation..."
wkhtmltopdf --version

# Create XDG_RUNTIME_DIR fix for odoo user
echo "Setting up XDG_RUNTIME_DIR..."
sudo mkdir -p /run/odoo
sudo chown odoo:odoo /run/odoo 2>/dev/null || sudo chown root:root /run/odoo
sudo chmod 700 /run/odoo

# Update Odoo systemd service to include environment variable
echo "Updating Odoo systemd service..."
if [ -f /etc/systemd/system/odoo.service ]; then
    # Remove any existing XDG_RUNTIME_DIR lines
    sudo sed -i '/XDG_RUNTIME_DIR/d' /etc/systemd/system/odoo.service
    # Add the environment variable after [Service]
    sudo sed -i '/\[Service\]/a Environment="XDG_RUNTIME_DIR=/run/odoo"' /etc/systemd/system/odoo.service
    sudo systemctl daemon-reload
    echo "Service file updated successfully"
else
    echo "WARNING: Odoo service file not found at /etc/systemd/system/odoo.service"
    echo "Please manually add this line to your Odoo service file under [Service]:"
    echo "  Environment=\"XDG_RUNTIME_DIR=/run/odoo\""
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Restart Odoo: sudo systemctl restart odoo"
echo "2. Check logs: sudo journalctl -u odoo -f"
echo "3. Verify: wkhtmltopdf --version (should show 'with patched qt')"