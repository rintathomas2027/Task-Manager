#!/bin/bash
# setup_ec2.sh - Automatic Deployment Script for Task Manager

# Update System
sudo apt update && sudo apt upgrade -y

# Install Dependencies
sudo apt install -y python3-pip python3-venv nginx mysql-server git libmysqlclient-dev pkg-config

# Configure MySQL
sudo mysql -e "CREATE DATABASE IF NOT EXISTS task_manager_db;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY 'ajce';"
sudo mysql -e "GRANT ALL PRIVILEGES ON task_manager_db.* TO 'root'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Clone Project
cd /home/ubuntu
git clone https://github.com/rintathomas2027/Task-Manager.git
cd Task-Manager

# Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Run Migrations
python manage.py migrate

# Collect Static Files
python manage.py collectstatic --noinput

# Import Data (Instructions)
echo "--------------------------------------------------------"
echo "SETUP ALMOST COMPLETE!"
echo "1. Upload your 'db_backup.sql' to this server."
echo "2. Run: mysql -u root -pajce task_manager_db < db_backup.sql"
echo "3. Update ALLOWED_HOSTS in settings.py with your EC2 IP."
echo "--------------------------------------------------------"
