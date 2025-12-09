# AWS Lambda - EC2 Instance Terminator

Python Lambda function to terminate one or multiple EC2 instances with detailed status reporting.

## Files

- `lambda_function.py` - Main Lambda function code
- `requirements.txt` - Python dependencies
- `test_event.json` - Sample event for testing multiple instances
- `test_single_instance.json` - Sample event for testing a single instance

## Usage

The Lambda function accepts instance IDs in multiple ways:

### 1. Single Instance
```json
{
  "instance_id": "i-1234567890abcdef0"
}
```

### 2. Multiple Instances (Recommended)
```json
{
  "instance_ids": [
    "i-1234567890abcdef0",
    "i-0987654321fedcba0",
    "i-abcdef1234567890"
  ]
}
```

### 3. Environment Variable
Set `INSTANCE_IDS` in Lambda configuration (comma-separated):
```
INSTANCE_IDS=i-1234567890abcdef0,i-0987654321fedcba0
```

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

The function returns detailed status for each instance:

### Success Response (200 - All Successful):
```json
{
  "statusCode": 200,
  "body": {
    "total_requested": 3,
    "successful": [
      {
        "instance_id": "i-1234567890abcdef0",
        "previous_state": "running",
        "current_state": "shutting-down",
        "details": {
          "state": "running",
          "instance_type": "t2.micro",
          "launch_time": "2025-12-09T10:30:00",
          "tags": {"Name": "WebServer"}
        }
      }
    ],
    "failed": [],
    "blocked": [],
    "summary": {
      "total_requested": 3,
      "successful_terminations": 3,
      "blocked_terminations": 0,
      "failed_terminations": 0
    }
  }
}
```

### Partial Success (207 - Some Blocked):
```json
{
  "statusCode": 207,
  "body": {
    "total_requested": 3,
    "successful": [
      {
        "instance_id": "i-1234567890abcdef0",
        "previous_state": "running",
        "current_state": "shutting-down"
      }
    ],
    "blocked": [
      {
        "instance_id": "i-0987654321fedcba0",
        "reason": "Termination protection enabled or insufficient permissions",
        "error_code": "OperationNotPermitted",
        "error_message": "The instance 'i-0987654321fedcba0' may not be terminated..."
      },
      {
        "instance_id": "i-abcdef1234567890",
        "reason": "Instance does not exist",
        "error_code": "InvalidInstanceID.NotFound"
      }
    ],
    "summary": {
      "total_requested": 3,
      "successful_terminations": 1,
      "blocked_terminations": 2,
      "failed_terminations": 0
    }
  }
}
```

## Status Codes

- **200**: All instances terminated successfully
- **207**: Partial success (some succeeded, some blocked/failed)
- **400**: All instances failed or no instances provided

## Blocked Reasons

The function identifies why terminations are blocked:

- **Termination protection enabled** - Instance has termination protection
- **Instance does not exist** - Invalid instance ID
- **Insufficient IAM permissions** - Lambda role lacks permissions
- **Instance already terminated/terminating** - Instance in final state
