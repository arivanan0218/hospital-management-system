#!/bin/bash

# Script to get AWS Account ID and other required information

echo "🔍 Getting AWS Account Information..."
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first"
    exit 1
fi

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)

echo "✅ AWS Account Information:"
echo "   Account ID: $ACCOUNT_ID"
echo "   Region: $REGION"
echo "   User/Role: $USER_ARN"
echo ""

echo "📋 Copy these values to your GitHub Secrets:"
echo "   AWS_ACCOUNT_ID: $ACCOUNT_ID"
echo "   AWS_REGION: $REGION"
echo ""

echo "🔧 Next steps:"
echo "1. Go to your GitHub repository → Settings → Secrets and variables → Actions"
echo "2. Add the AWS_ACCOUNT_ID secret with value: $ACCOUNT_ID"
echo "3. Add other required secrets as mentioned in DEPLOYMENT.md"
