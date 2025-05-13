#!/bin/bash

# Configuration
AWS_REGION="ca-central-1"
ROLE_NAME="ecsTaskExecutionRole"

# Create the IAM role
echo "Creating IAM role..."
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }' || echo "Role already exists, continuing..."

# Attach the policy to the role
echo "Attaching policy to role..."
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name ecsTaskExecutionRolePolicy \
    --policy-document file://aws/ecs/task-execution-role.json

echo "IAM role setup completed!"
