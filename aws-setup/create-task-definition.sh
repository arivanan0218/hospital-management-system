#!/bin/bash

# Create ECS Task Definition and Service

set -e

AWS_REGION="us-east-1"
CLUSTER_NAME="hospital-cluster"
SERVICE_NAME="hospital-management-service"
TASK_DEFINITION_NAME="hospital-task-definition"
TARGET_GROUP_ARN="YOUR_TARGET_GROUP_ARN"  # Replace with actual ARN from setup-infrastructure.sh output
SUBNET_1_ID="YOUR_SUBNET_1_ID"  # Replace with actual subnet ID
SUBNET_2_ID="YOUR_SUBNET_2_ID"  # Replace with actual subnet ID
SG_ID="YOUR_SECURITY_GROUP_ID"  # Replace with actual security group ID

echo "🔧 Creating ECS Task Definition and Service..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Replace ACCOUNT_ID in task definition
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" task-definition.json

# Create CloudWatch log group
aws logs create-log-group \
    --log-group-name /ecs/hospital-management \
    --region $AWS_REGION \
    || echo "Log group might already exist"

# Register task definition
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --region $AWS_REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "Created Task Definition: $TASK_DEF_ARN"

# Create ECS service
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_DEFINITION_NAME \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1_ID,$SUBNET_2_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=hospital-frontend,containerPort=80" \
    --region $AWS_REGION

echo "✅ ECS Service created successfully!"
echo ""
echo "📋 Service Details:"
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Task Definition: $TASK_DEF_ARN"
echo ""
echo "🔧 Next steps:"
echo "1. Wait for the service to stabilize (5-10 minutes)"
echo "2. Check the Application Load Balancer DNS name for your application URL"
echo "3. Set up GitHub secrets and push your code to trigger CI/CD"
