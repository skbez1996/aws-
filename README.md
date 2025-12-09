# AWS Lambda - EC2 Instance Terminator

Python Lambda function to terminate an EC2 instance.

## Files

- `lambda_function.py` - Main Lambda function code
- `requirements.txt` - Python dependencies
- `test_event.json` - Sample event for testing

## Usage

The Lambda function accepts the instance ID in two ways:

1. **Via event parameter:**
```json
{
  "instance_id": "i-1234567890abcdef0"
}
```

2. **Via environment variable:** Set `INSTANCE_ID` in Lambda configuration

## IAM Permissions Required

The Lambda execution role needs the following permissions:

```json
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
```

## Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt -t .
```

2. Create deployment package:
```bash
zip -r lambda_function.zip lambda_function.py boto3* botocore*
```

3. Deploy to AWS Lambda via AWS CLI:
```bash
aws lambda create-function \
  --function-name terminate-ec2-instance \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip
```

## Response Format

### Success (200):
```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully initiated termination of instance i-1234567890abcdef0",
    "instance_id": "i-1234567890abcdef0",
    "previous_state": "running",
    "current_state": "shutting-down"
  }
}
```

### Error (400/500):
```json
{
  "statusCode": 400,
  "body": {
    "error": "No instance_id provided in event or INSTANCE_ID environment variable"
  }
}
```
