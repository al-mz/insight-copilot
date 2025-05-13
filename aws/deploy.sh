#!/bin/bash

# Configuration
AWS_REGION="ca-central-1"  # Change this to your desired region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_BACKEND="insight-copilot-backend"
ECR_REPOSITORY_FRONTEND="insight-copilot-frontend"
ECS_CLUSTER="insight-copilot-cluster"
ECS_SERVICE="insight-copilot-service"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it first."
    echo "On macOS: brew install jq"
    echo "On Ubuntu/Debian: sudo apt-get install jq"
    exit 1
fi

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repositories if they don't exist
echo "Setting up ECR repositories..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_BACKEND || aws ecr create-repository --repository-name $ECR_REPOSITORY_BACKEND
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_FRONTEND || aws ecr create-repository --repository-name $ECR_REPOSITORY_FRONTEND

# Build and push backend image
echo "Building and pushing backend image..."
docker build -t $ECR_REPOSITORY_BACKEND ./backend
docker tag $ECR_REPOSITORY_BACKEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_BACKEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_BACKEND:latest

# Build and push frontend image
echo "Building and pushing frontend image..."
docker build -t $ECR_REPOSITORY_FRONTEND ./frontend
docker tag $ECR_REPOSITORY_FRONTEND:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_FRONTEND:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_FRONTEND:latest

# Update task definition
echo "Updating task definition..."
TASK_DEF_PATH="aws/ecs/task-definition.json"
if [ ! -f "$TASK_DEF_PATH" ]; then
    echo "Error: Task definition file not found at $TASK_DEF_PATH"
    exit 1
fi

# Register new task definition
echo "Registering task definition..."
TASK_DEFINITION=$(aws ecs register-task-definition --cli-input-json file://$TASK_DEF_PATH)
if [ $? -ne 0 ]; then
    echo "Error: Failed to register task definition"
    exit 1
fi

TASK_REVISION=$(echo $TASK_DEFINITION | jq -r '.taskDefinition.revision')
if [ -z "$TASK_REVISION" ]; then
    echo "Error: Failed to get task revision"
    exit 1
fi

# Check if service exists
SERVICE_EXISTS=$(aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --query 'services[0].status' --output text 2>/dev/null)

if [ "$SERVICE_EXISTS" = "ACTIVE" ]; then
    # Update existing service
    echo "Updating existing ECS service..."
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --task-definition insight-copilot:$TASK_REVISION --force-new-deployment
else
    # Create new service
    echo "Creating new ECS service..."
    # Get VPC and subnet information
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0:2].SubnetId" --output text | tr '\t' ',')
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=insight-copilot-sg" --query "SecurityGroups[0].GroupId" --output text)

    aws ecs create-service \
        --cluster $ECS_CLUSTER \
        --service-name $ECS_SERVICE \
        --task-definition insight-copilot:$TASK_REVISION \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"
fi

echo "Deployment completed successfully!"
