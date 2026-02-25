# Sales Analytics Chatbot – Deployment Guide

## 🚀 AWS Deployment Architecture

```
┌─────────────────┐
│  CloudFront CDN │ (Frontend Caching)
└────────┬────────┘
         │
    ┌────▼─────┐
    │  S3 Bucket│ (React SPA)
    └────┬─────┘
         │
    ┌────▼─────────────────┐
    │   API Gateway        │ (Auth, Rate Limiting)
    └────┬─────────────────┘
         │
    ┌────▼──────────┐
    │  EC2 / ECS    │ (FastAPI App)
    └────┬──────────┘
         │
    ┌────▼──────────────┐
    │  RDS (PostgreSQL) │ (Data)
    └───────────────────┘
```

## 1️⃣ Backend Deployment (EC2)

### Prerequisites
- EC2 instance (t3.medium+, Ubuntu 22.04)
- Security group allowing:
  - Inbound: ports 80, 443
  - Outbound: RDS, Bedrock endpoint

### Steps

```bash
# SSH into EC2
ssh -i fastapi-key.pem ubuntu@3.87.81.95

# Install dependencies
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv postgresql-client curl

# Clone/download code
cd /home/ubuntu
git clone <repo>  # or upload folder
cd sales-analytics

# Setup Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
nano .env  # Add AWS_REGION, BEDROCK_MODEL_ID, RDS credentials

# Test DB connection
python init_db.py

# Install systemd service
sudo tee /etc/systemd/system/sales-chatbot.service > /dev/null <<EOF
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
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable sales-chatbot
sudo systemctl start sales-chatbot
sudo systemctl status sales-chatbot
```

### Verify

```bash
curl http://localhost:8000/health
```

---

## 2️⃣ Frontend Deployment (S3 + CloudFront)

### Steps

```bash
# Build React app
cd frontend
npm install
npm run build  # Creates dist/ folder

# Create S3 bucket
aws s3api create-bucket \
  --bucket sales-chatbot-ui \
  --region us-east-1

# Upload build files
aws s3 sync dist/ s3://sales-chatbot-ui/ --delete

# Create CloudFront distribution
# 1. Go to AWS Console → CloudFront
# 2. Create distribution
#    - Origin: S3 bucket
#    - Default root object: index.html
#    - ViewerProtocolPolicy: Redirect HTTP to HTTPS
#    - Custom error responses:
#      - 404 → index.html (for SPA routing)

# Get CloudFront domain
aws cloudfront list-distributions --query "DistributionList.Items[0].DomainName"
```

---

## 3️⃣ RDS Setup

### Create PostgreSQL Instance

```bash
# AWS CLI
aws rds create-db-instance \
  --db-instance-identifier salesdb \
  --engine postgres \
  --engine-version 14.8 \
  --db-instance-class db.t3.micro \
  --allocated-storage 20 \
  --master-username postgres \
  --master-user-password "<STRONG_PASSWORD>" \
  --publicly-accessible false \
  --storage-encrypted true \
  --region us-east-1

# Wait 5-10 minutes for creation
```

### Security
- Database subnet: Private VPC
- Security group: Allow EC2 only (port 5432)
- Enable automated backups (7 days)
- Enable Enhanced Monitoring

### Connect from EC2

```bash
psql -h salesdb.xxxxx.rds.amazonaws.com -U postgres -d salesdb
```

---

## 4️⃣ IAM Permissions

### EC2 Instance Role Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-east-1:*:*"
    }
  ]
}
```

---

## 5️⃣ API Gateway (Optional, for Auth)

```bash
# Create REST API
aws apigateway create-rest-api \
  --name sales-analytics \
  --description "Sales Chatbot API"

# Add JWT authorizer
# 1. Console → API Gateway → Create Authorizer
# 2. Type: TOKEN
# 3. Token validation expression: Authorization header
# 4. Handler: Lambda (optional)

# Create resource /chat
# Add POST method → Integration → HTTP → Endpoint: http://ec2:8000/chat
# Add Authorization: JWT
```

---

## 6️⃣ Monitoring & Logging

### CloudWatch

```bash
# View app logs
aws logs tail /aws/ec2/sales-chatbot --follow

# Set up alarms
aws cloudwatch put-metric-alarm \
  --alarm-name sales-chatbot-error \
  --metric-name Errors \
  --namespace AWS/ECS \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

### Application Logging

- Backend logs to `stdout` (captured by systemd)
- Frontend logs to browser console
- Configure CloudWatch agent on EC2 for centralized logs

---

## 7️⃣ HTTPS & SSL

### Using AWS Certificate Manager

```bash
# Request certificate
aws acm request-certificate \
  --domain-name api.yourdomain.com \
  --validation-method DNS

# Add DNS CNAME records (from email)
# Wait for validation (~5 minutes)

# Attach cert to:
# - ALB (if using) or API Gateway
# - CloudFront distribution
```

---

## 8️⃣ CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy Backend
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            cd sales-analytics
            git pull
            source .venv/bin/activate
            pip install -r requirements.txt
            python init_db.py
            sudo systemctl restart sales-chatbot

      - name: Deploy Frontend
        run: |
          cd frontend
          npm install
          npm run build
          aws s3 sync dist/ s3://sales-chatbot-ui/ --delete
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 📊 Performance Tuning

### Backend
- RDS: Enable read replicas for scaling
- FastAPI: Use `uvicorn` with `--workers` matching CPU cores
- Bedrock: Cache prompts for repeated questions

### Frontend
- Vite build optimization (code splitting, compression)
- CloudFront edge caching (TTL 1 hour)
- Lazy load React components

### Database
- Index on `sale_date`, `region`, `category`
- Partitioning by date for large tables
- Connection pooling via SQLAlchemy (pool_size)

---

## 🔒 Security Best Practices

1. **Secrets Management**
   - Use AWS Secrets Manager for DB/API keys
   - Rotate credentials every 90 days

2. **Network**
   - VPC isolation, no public DB
   - Use security groups, NACLs
   - WAF rules on CloudFront

3. **Code**
   - SQL validation (already implemented)
   - Rate limiting on API Gateway
   - CORS restricted to CloudFront domain

4. **Compliance**
   - Enable MFA on AWS Console
   - CloudTrail for audit logs
   - Data encryption at rest & in transit

---

## 📝 Cost Estimation

| Component | Size | Monthly Cost |
|-----------|------|---|
| EC2 (t3.medium) | 1 instance | ~$30 |
| RDS (db.t3.micro) | 20GB | ~$15 |
| S3 + CloudFront | 10GB traffic | ~$10 |
| Data transfer | ~100GB | ~$10 |
| **Total** | | **~$65** |

---

## 🚨 Troubleshooting

### Backend won't start
```bash
sudo systemctl status sales-chatbot
sudo journalctl -u sales-chatbot -n 50
```

### DB connection timeout
```bash
# Test from EC2
psql -h <rds-endpoint> -U postgres -d salesdb -c "SELECT 1"
```

### Frontend blank page
- Check CloudFront cache invalidation
- Verify API endpoint in CloudFront
- Check S3 bucket CORS policy

### Bedrock `AccessDenied`
- Verify IAM role attached to EC2
- Check region matches (us-east-1)
- Ensure model ID is correct

---

## 📚 References

- [AWS EC2 Launch Types](https://docs.aws.amazon.com/ec2/)
- [RDS PostgreSQL Ops](https://docs.aws.amazon.com/rds/latest/userguide/USER_PostgreSQL.html)
- [Bedrock API](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [CloudFront SPA Setup](https://docs.aws.amazon.com/S3/latest/dev/WebsiteHosting.html)
