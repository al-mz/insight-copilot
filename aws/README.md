# AWS Deployment Guide for Insight Copilot

This guide explains how to deploy Insight Copilot to AWS using ECS (Elastic Container Service) and ECR (Elastic Container Registry).

## Prerequisites

1. AWS CLI installed and configured with appropriate credentials
2. Docker installed and running locally
3. `jq` command-line tool installed
   ```bash
   # On macOS:
   brew install jq

   # On Ubuntu/Debian:
   sudo apt-get install jq
   ```

## Deployment Steps

### 1. Infrastructure Setup

First, set up the required AWS infrastructure:

```bash
# Make scripts executable
chmod +x aws/setup-ecs.sh
chmod +x aws/setup-alb.sh
chmod +x aws/deploy.sh

# Set up ECS cluster and security groups
./aws/setup-ecs.sh

# Set up Application Load Balancer
./aws/setup-alb.sh
```

### 2. Deploy the Application

Deploy the application to ECS:

```bash
./aws/deploy.sh
```

This script will:
- Build and push Docker images to ECR
- Create/update the ECS task definition
- Create/update the ECS service

### 3. Access the Application

After deployment, the application will be available at the ALB URL provided in the setup output. The URL format will be:
```
http://<alb-dns-name>
```

Note: It may take a few minutes for:
- The ALB to become active
- The ECS service to register the container
- The health checks to pass

## Monitoring Deployment

You can monitor the deployment status in the AWS Console:

1. **ECS Status**:
   - ECS → Clusters → insight-copilot-cluster → Services
   - Check service status and running tasks

2. **Load Balancer Status**:
   - EC2 → Load Balancers → insight-copilot-alb
   - Verify the ALB is active

3. **Target Group Health**:
   - EC2 → Target Groups → insight-copilot-tg
   - Check target health status

## Architecture Overview

The deployment uses the following AWS services:

- **ECS (Fargate)**: Runs the containers without managing servers
- **ECR**: Stores Docker images
- **ALB**: Routes traffic to the frontend container
- **CloudWatch**: Stores container logs
- **VPC**: Provides networking for the containers

### Network Flow

1. Internet traffic → ALB (port 80)
2. ALB → Frontend container (port 3000)
3. Frontend container → Backend container (internal ECS network)

## Troubleshooting

### Common Issues

1. **Container Health Check Failures**:
   - Check container logs in CloudWatch
   - Verify the application is listening on the correct port

2. **ALB Not Active**:
   - Check security group rules
   - Verify subnet configurations

3. **ECS Service Not Starting**:
   - Check task definition
   - Verify IAM roles and permissions

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster insight-copilot-cluster --services insight-copilot-service

# View container logs
aws logs get-log-events --log-group-name /ecs/insight-copilot --log-stream-name <stream-name>

# Check ALB status
aws elbv2 describe-load-balancers --names insight-copilot-alb
```

## Cleanup

To remove all AWS resources:

1. Delete the ECS service and cluster
2. Delete the ALB and target group
3. Remove the ECR repositories
4. Delete the security groups
5. Remove the CloudWatch log group

## Security Notes

- The ALB is configured to accept HTTP traffic on port 80
- For production, consider:
  - Adding HTTPS support
  - Restricting security group access
  - Using AWS WAF for additional protection
  - Implementing proper IAM roles and policies
