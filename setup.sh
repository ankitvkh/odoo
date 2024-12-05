#!/bin/bash

# Set up environment variables
ODOO_VERSION="18.0"  # Change this to your desired Odoo version
PYTHON_VERSION="3.10"  # Change this to your desired Python version
WORK_DIR="$HOME/odoo-build"
VENV_DIR="$WORK_DIR/venv"
ADDONS_DIR="$WORK_DIR/custom_addons"

# Create working directory
echo "Starting in: $PWD"
mkdir -p $WORK_DIR
cd $WORK_DIR
echo "Changed to: $PWD"

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    git \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-client \
    libpq-dev \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libtiff5-dev \
    libjpeg8-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    node-less \
    npm

# Create and activate virtual environment
python${PYTHON_VERSION} -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Clone Odoo repository
git clone -b demo https://github.com/ankitvkh/odoo.git
cd odoo
echo "Now in: $PWD"

# Install wheel and setuptools
pip install --upgrade pip wheel setuptools

# Install Odoo dependencies
pip install -r requirements.txt

# Create custom_addons directory and copy your addons
mkdir -p $ADDONS_DIR
# Copy your custom addons here
cp -r addons/* $ADDONS_DIR/

# Create a proper setup.py file
# cat << EOF > setup.py
# from setuptools import setup, find_packages
# import os

# def find_addons_packages():
#     """Find Odoo addon packages"""
#     packages = []
#     for addon in os.listdir('addons'):
#         if os.path.isdir(os.path.join('addons', addon)):
#             packages.append(f"odoo.addons.{addon}")
#     return packages

# def find_addon_files():
#     """Find all non-Python files in addons"""
#     data_files = []
#     for root, _, files in os.walk('addons'):
#         for file in files:
#             if not file.endswith('.py'):
#                 data_files.append(os.path.join(root, file))
#     return data_files

# packages = ['odoo'] + find_addons_packages()
# data_files = find_addon_files()

# setup(
#     name='odoo',
#     version='$ODOO_VERSION',
#     packages=packages,
#     package_dir={'odoo': '.'},
#     package_data={
#         'odoo': ['addons/**/*'],
#     },
#     include_package_data=True,
#     python_requires='>=3.10',
#     install_requires=[
#         'psycopg2-binary',
#         'Werkzeug',
#         'Jinja2',
#         'Pillow',
#         'lxml',
#         'python-dateutil',
#         'pytz',
#         'polib',
#         'PyPDF2',
#         'reportlab',
#         'requests',
#         'passlib',
#         'docutils',
#         'num2words',
#         'babel',
#     ],
# )
# EOF

# # Create __init__.py if it doesn't exist
# touch __init__.py

# # Create odoo directory structure if it doesn't exist
# mkdir -p odoo
# touch odoo/__init__.py

# # Build the wheel file
# python setup.py bdist_wheel

# # The wheel file will be available in the dist directory
# echo "Wheel file created in ./dist directory"
# ls -l dist/
