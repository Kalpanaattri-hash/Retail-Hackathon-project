#!/bin/bash
# Production setup and deployment script for AWS

set -e

echo "========================================="
echo "Sales Analytics Chatbot - AWS Deployment"
echo "========================================="

if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Get inputs
read -p "Enter EC2 instance public IP: " EC2_IP
read -p "Enter RDS endpoint: " RDS_HOST
read -s -p "Enter RDS password: " RDS_PASSWORD
echo ""

# SSH into EC2
echo "[1] Updating system..."
ssh -i ../fastapi-key.pem ubuntu@$EC2_IP << 'EOF'
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y python3.10 python3-pip python3-venv postgresql-client curl git nginx

    # Clone repo
    cd /home/ubuntu
    git clone <REPO_URL>  # Update with your repo
    cd sales-analytics

    # Setup Python
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    # Configure .env
    cat > .env << ENVEOF
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
DB_HOST=$RDS_HOST
DB_PORT=5432
DB_NAME=salesdb
DB_USER=postgres
DB_PASSWORD=$RDS_PASSWORD
DB_SSL_MODE=require
ENVEOF

    # Initialize DB
    python init_db.py

    # Install systemd service
    sudo tee /etc/systemd/system/sales-chatbot.service > /dev/null <<'SVCEOF'
[Unit]
Description=Sales Analytics Chatbot
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/sales-analytics
Environment="PATH=/home/ubuntu/sales-analytics/.venv/bin"
ExecStart=/home/ubuntu/sales-analytics/.venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

    sudo systemctl daemon-reload
    sudo systemctl enable sales-chatbot
    sudo systemctl start sales-chatbot

    # Configure Nginx
    sudo tee /etc/nginx/sites-available/sales-chatbot > /dev/null <<'NGXEOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGXEOF

    sudo ln -sf /etc/nginx/sites-available/sales-chatbot /etc/nginx/sites-enabled/
    sudo systemctl restart nginx

    echo "Backend deployed and running!"
EOF

echo "[2] Deploying frontend..."
cd frontend
npm install
npm run build

# Upload to S3
aws s3 sync dist/ s3://sales-chatbot-ui-${EC2_IP}/ --delete

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Backend: http://$EC2_IP"
echo "Frontend: Uploading to S3..."
echo "========================================="
