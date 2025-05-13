#!/bin/bash

# Configuration
AWS_REGION="ca-central-1"
CLUSTER_NAME="insight-copilot-cluster"
SERVICE_NAME="insight-copilot-service"

# Create ECS cluster
echo "Creating ECS cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME || echo "Cluster already exists"

# Create CloudWatch log group
echo "Creating CloudWatch log group..."
aws logs create-log-group --log-group-name /ecs/insight-copilot || echo "Log group already exists"

# Create security group for the service
echo "Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name insight-copilot-sg \
    --description "Security group for Insight Copilot" \
    --vpc-id $VPC_ID \
    --query "GroupId" \
    --output text) || echo "Security group already exists"

# Allow inbound traffic
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 || echo "Port 80 rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 || echo "Port 443 rule already exists"

# Get subnet IDs
SUBNET_IDS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query "Subnets[0:2].SubnetId" \
    --output text | tr '\t' ',')

echo "ECS infrastructure setup completed!"
echo "Next steps:"
echo "1. Run ./aws/deploy.sh to create the task definition and service"
