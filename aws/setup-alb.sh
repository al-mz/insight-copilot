#!/bin/bash

# Configuration
AWS_REGION="ca-central-1"
CLUSTER_NAME="insight-copilot-cluster"
SERVICE_NAME="insight-copilot-service"
ALB_NAME="insight-copilot-alb"
TARGET_GROUP_NAME="insight-copilot-tg"

# Get VPC and subnet information
echo "Getting VPC and subnet information..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0:2].SubnetId" --output text | tr '\t' ' ')

# Create security group for ALB
echo "Creating security group for ALB..."
ALB_SG_ID=$(aws ec2 create-security-group \
    --group-name insight-copilot-alb-sg \
    --description "Security group for Insight Copilot ALB" \
    --vpc-id $VPC_ID \
    --query "GroupId" \
    --output text) || echo "Security group already exists"

# Allow inbound traffic to ALB
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 || echo "Port 80 rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 || echo "Port 443 rule already exists"

# Create ALB
echo "Creating Application Load Balancer..."
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name $ALB_NAME \
    --subnets $SUBNET_IDS \
    --security-groups $ALB_SG_ID \
    --scheme internet-facing \
    --type application \
    --query "LoadBalancers[0].LoadBalancerArn" \
    --output text)

# Create target group
echo "Creating target group..."
TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
    --name $TARGET_GROUP_NAME \
    --protocol HTTP \
    --port 3000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path / \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --query "TargetGroups[0].TargetGroupArn" \
    --output text)

# Create listener
echo "Creating listener..."
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN

# Update ECS service to use the target group
echo "Updating ECS service to use the target group..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --load-balancers targetGroupArn=$TARGET_GROUP_ARN,containerName=frontend,containerPort=3000

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names $ALB_NAME \
    --query "LoadBalancers[0].DNSName" \
    --output text)

echo "Setup completed!"
echo "Your application will be available at: http://$ALB_DNS"
echo "Note: It may take a few minutes for the ALB to become active and for the containers to start."
