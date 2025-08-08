@echo off
REM Create ECS Task Definition and Service for Windows

echo 🔧 Creating ECS Task Definition and Service...

REM Configuration variables (updated with your actual values)
set AWS_REGION=us-east-1
set CLUSTER_NAME=hospital-cluster
set SERVICE_NAME=hospital-management-service
set TASK_DEFINITION_NAME=hospital-task-definition
set TARGET_GROUP_ARN=arn:aws:elasticloadbalancing:us-east-1:324037286635:targetgroup/hospital-targets/6297cfcbdce60c66
set SUBNET_1_ID=subnet-0a03f0b465b06b5ff
set SUBNET_2_ID=subnet-07c708f6f5f6e4b8b
set SG_ID=sg-044d457d3d4587709

echo 📋 Configuration:
echo Cluster: %CLUSTER_NAME%
echo Service: %SERVICE_NAME%
echo Task Definition: %TASK_DEFINITION_NAME%
echo Target Group: %TARGET_GROUP_ARN%
echo Subnets: %SUBNET_1_ID%, %SUBNET_2_ID%
echo Security Group: %SG_ID%

REM Get AWS account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query "Account" --output text') do set ACCOUNT_ID=%%i
echo Account ID: %ACCOUNT_ID%

REM Create a temporary task definition with the correct account ID
echo 🔄 Preparing task definition...
powershell -Command "(Get-Content task-definition.json) -replace 'ACCOUNT_ID', '%ACCOUNT_ID%' | Set-Content task-definition-updated.json"

echo.
echo ⚠️  IMPORTANT: You need to update the API keys in task-definition-updated.json
echo.
echo Please replace the following placeholders with your actual API keys:
echo - YOUR_GEMINI_API_KEY
echo - YOUR_CLAUDE_API_KEY (optional)
echo - YOUR_OPENAI_API_KEY (optional)
echo - YOUR_GROQ_API_KEY (optional)
echo - YOUR_GOOGLE_API_KEY (optional)
echo.
echo Opening the file for editing...
notepad task-definition-updated.json
echo.
echo Press any key when you've updated the API keys...
pause

REM Register task definition
echo 📝 Registering task definition...
for /f "tokens=*" %%i in ('aws ecs register-task-definition --cli-input-json file://task-definition-updated.json --region %AWS_REGION% --query "taskDefinition.taskDefinitionArn" --output text') do set TASK_DEF_ARN=%%i
echo Created Task Definition: %TASK_DEF_ARN%

REM Check if service already exists
aws ecs describe-services --cluster %CLUSTER_NAME% --services %SERVICE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Service already exists, updating...
    aws ecs update-service ^
        --cluster %CLUSTER_NAME% ^
        --service %SERVICE_NAME% ^
        --task-definition %TASK_DEFINITION_NAME% ^
        --desired-count 1
) else (
    echo 🚀 Creating ECS service...
    aws ecs create-service ^
        --cluster %CLUSTER_NAME% ^
        --service-name %SERVICE_NAME% ^
        --task-definition %TASK_DEFINITION_NAME% ^
        --desired-count 1 ^
        --launch-type FARGATE ^
        --platform-version LATEST ^
        --network-configuration "awsvpcConfiguration={subnets=[%SUBNET_1_ID%,%SUBNET_2_ID%],securityGroups=[%SG_ID%],assignPublicIp=ENABLED}" ^
        --load-balancers "targetGroupArn=%TARGET_GROUP_ARN%,containerName=hospital-frontend,containerPort=80" ^
        --region %AWS_REGION%
)

echo ✅ ECS Service setup complete!
echo.
echo 📋 Service Details:
echo Cluster: %CLUSTER_NAME%
echo Service: %SERVICE_NAME%
echo Task Definition: %TASK_DEF_ARN%
echo.
echo 🌐 Getting your application URL...
for /f "tokens=*" %%i in ('aws elbv2 describe-load-balancers --names hospital-alb --query "LoadBalancers[0].DNSName" --output text 2^>nul') do set ALB_DNS=%%i
if defined ALB_DNS (
    echo Application URL: http://%ALB_DNS%
) else (
    echo ALB DNS not found, check manually with: aws elbv2 describe-load-balancers --names hospital-alb
)
echo.
echo 🔧 Next steps:
echo 1. Wait for the service to stabilize (5-10 minutes)
echo 2. Set up GitHub secrets for CI/CD:
echo    - AWS_ACCESS_KEY_ID
echo    - AWS_SECRET_ACCESS_KEY
echo    - GEMINI_API_KEY
echo    - Other optional API keys
echo 3. Push your code to docker branch to trigger deployment
echo.
echo 📊 Monitor your deployment:
echo aws ecs describe-services --cluster %CLUSTER_NAME% --services %SERVICE_NAME%

pause
