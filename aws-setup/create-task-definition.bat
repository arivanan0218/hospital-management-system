@echo off
REM Create ECS Task Definition and Service for Windows

echo 🔧 Creating ECS Task Definition and Service...

set AWS_REGION=us-east-1
set CLUSTER_NAME=hospital-cluster
set SERVICE_NAME=hospital-management-service
set TASK_DEFINITION_NAME=hospital-task-definition

REM Load values from previous script
if exist aws-values.bat (
    call aws-values.bat
    echo ✅ Loaded AWS values from previous setup
) else (
    echo ❌ aws-values.bat not found. Please run setup-infrastructure.bat first.
    pause
    exit /b 1
)

REM Get AWS account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query "Account" --output text') do set ACCOUNT_ID=%%i
echo AWS Account ID: %ACCOUNT_ID%

REM Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/hospital-management --region %AWS_REGION% 2>nul || echo Log group might already exist

REM Replace ACCOUNT_ID in task definition
powershell -Command "(Get-Content task-definition.json) -replace 'ACCOUNT_ID', '%ACCOUNT_ID%' | Set-Content task-definition-updated.json"

REM Register task definition
for /f "tokens=*" %%i in ('aws ecs register-task-definition --cli-input-json file://task-definition-updated.json --region %AWS_REGION% --query "taskDefinition.taskDefinitionArn" --output text') do set TASK_DEF_ARN=%%i

echo Created Task Definition: %TASK_DEF_ARN%

REM Create ECS service
aws ecs create-service --cluster %CLUSTER_NAME% --service-name %SERVICE_NAME% --task-definition %TASK_DEFINITION_NAME% --desired-count 1 --launch-type FARGATE --platform-version LATEST --network-configuration "awsvpcConfiguration={subnets=[%SUBNET_1_ID%,%SUBNET_2_ID%],securityGroups=[%SG_ID%],assignPublicIp=ENABLED}" --load-balancers "targetGroupArn=%TARGET_GROUP_ARN%,containerName=hospital-frontend,containerPort=80" --region %AWS_REGION%

if %errorlevel% equ 0 (
    echo ✅ ECS Service created successfully!
) else (
    echo ❌ Failed to create ECS service. Check the error above.
    pause
    exit /b 1
)

echo.
echo 📋 Service Details:
echo Cluster: %CLUSTER_NAME%
echo Service: %SERVICE_NAME%
echo Task Definition: %TASK_DEF_ARN%
echo.

REM Get ALB DNS name
for /f "tokens=*" %%i in ('aws elbv2 describe-load-balancers --names hospital-alb --query "LoadBalancers[0].DNSName" --output text 2^>nul') do set ALB_DNS=%%i

if not "%ALB_DNS%"=="None" (
    echo 🌐 Your application will be available at: http://%ALB_DNS%
    echo ⏳ Please wait 5-10 minutes for the service to fully start
) else (
    echo ⚠️ Could not retrieve ALB DNS name. Check AWS console.
)

echo.
echo 🔧 Next steps:
echo 1. Wait for the service to stabilize (5-10 minutes)
echo 2. Set up GitHub secrets in your repository
echo 3. Push your code to the docker branch to trigger CI/CD
echo.
echo 📊 Check service status:
echo aws ecs describe-services --cluster %CLUSTER_NAME% --services %SERVICE_NAME%
echo.
pause
