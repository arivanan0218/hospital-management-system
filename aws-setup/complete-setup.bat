@echo off
REM Complete the AWS setup with existing resources

echo 🔧 Completing AWS infrastructure setup...

REM Set variables with the values from your setup
set ALB_ARN=arn:aws:elasticloadbalancing:us-east-1:324037286635:loadbalancer/app/hospital-alb/2dd01cf07c312192
set TARGET_GROUP_ARN=arn:aws:elasticloadbalancing:us-east-1:324037286635:targetgroup/hospital-targets/6297cfcbdce60c66
set VPC_ID=vpc-02b9cb42b900c1742
set SUBNET_1_ID=subnet-0a03f0b465b06b5ff
set SUBNET_2_ID=subnet-07c708f6f5f6e4b8b
set SG_ID=sg-044d457d3d4587709

echo 📋 Using existing resources:
echo ALB ARN: %ALB_ARN%
echo Target Group ARN: %TARGET_GROUP_ARN%
echo VPC ID: %VPC_ID%
echo Subnet IDs: %SUBNET_1_ID%, %SUBNET_2_ID%
echo Security Group ID: %SG_ID%

REM Create listener for the ALB (if it doesn't exist)
echo 🔗 Creating ALB listener...
aws elbv2 create-listener ^
    --load-balancer-arn %ALB_ARN% ^
    --protocol HTTP ^
    --port 80 ^
    --default-actions Type=forward,TargetGroupArn=%TARGET_GROUP_ARN% ^
    2>nul || echo "Listener might already exist"

REM Check if ECS cluster exists, if not create it
echo 🐳 Checking ECS cluster...
aws ecs describe-clusters --clusters hospital-cluster >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating ECS cluster...
    aws ecs create-cluster ^
        --cluster-name hospital-cluster ^
        --capacity-providers FARGATE ^
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
) else (
    echo ✅ ECS cluster already exists
)

REM Create CloudWatch log group
echo 📊 Creating CloudWatch log group...
aws logs create-log-group ^
    --log-group-name /ecs/hospital-management ^
    --region us-east-1 ^
    2>nul || echo "Log group might already exist"

echo ✅ AWS infrastructure setup complete!
echo.
echo 📋 Summary of resources:
echo VPC ID: %VPC_ID%
echo Subnet IDs: %SUBNET_1_ID%, %SUBNET_2_ID%
echo Security Group ID: %SG_ID%
echo ALB ARN: %ALB_ARN%
echo Target Group ARN: %TARGET_GROUP_ARN%
echo.
echo 🔧 Next step: Update task definition and create ECS service
echo Run: create-task-definition.bat
