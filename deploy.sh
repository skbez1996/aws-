#!/bin/bash

# Deployment script for EC2 Terminator Lambda Function

set -e

FUNCTION_NAME="ec2-instance-terminator"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="LambdaEC2TerminatorRole"

echo "🚀 Starting Lambda deployment..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

# Create IAM role for Lambda if it doesn't exist
echo "🔐 Checking IAM role..."
if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "Creating IAM role: $ROLE_NAME"
    
    # Create trust policy
    cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Role for EC2 instance terminator Lambda function"
    
    # Attach policies
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    # Create and attach EC2 termination policy
    cat > /tmp/ec2-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:TerminateInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name EC2TerminatorPolicy \
        --policy-document file:///tmp/ec2-policy.json
    
    echo "⏳ Waiting 10 seconds for IAM role to propagate..."
    sleep 10
else
    echo "✅ IAM role already exists"
fi

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# Create deployment package
echo "📦 Creating deployment package..."
rm -f lambda_function.zip
zip -q lambda_function.zip lambda_function.py

# Check if function exists
echo "🔍 Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
    echo "♻️  Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_function.zip
    
    echo "⚙️  Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --timeout 30 \
        --memory-size 128
else
    echo "🆕 Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda_function.zip \
        --timeout 30 \
        --memory-size 128 \
        --description "Lambda function to terminate EC2 instances"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Function details:"
echo "   Name: $FUNCTION_NAME"
echo "   ARN: arn:aws:lambda:$(aws configure get region):${ACCOUNT_ID}:function:${FUNCTION_NAME}"
echo ""
echo "🧪 To test the function, run:"
echo "   aws lambda invoke --function-name $FUNCTION_NAME --payload file://test_event.json response.json"
echo ""
echo "💡 To set an environment variable for default instance ID:"
echo "   aws lambda update-function-configuration --function-name $FUNCTION_NAME --environment Variables={INSTANCE_ID=i-xxxxxxxxx}"
