import boto3
import json
import os

def lambda_handler(event, context):
    """
    Lambda function to terminate one or multiple EC2 instances.
    
    Environment Variables:
        INSTANCE_IDS: Comma-separated list of instance IDs (optional)
    
    Event Parameters:
        instance_id: Single instance ID (string)
        instance_ids: List of instance IDs (array)
    
    Returns:
        dict: Response with detailed status for each instance
    """
    
    # Initialize EC2 client
    ec2 = boto3.client('ec2')
    
    # Collect instance IDs from various sources
    instance_ids = []
    
    # Check for single instance_id
    if 'instance_id' in event:
        instance_ids.append(event['instance_id'])
    
    # Check for multiple instance_ids (array)
    if 'instance_ids' in event:
        if isinstance(event['instance_ids'], list):
            instance_ids.extend(event['instance_ids'])
        else:
            instance_ids.append(event['instance_ids'])
    
    # Check environment variable
    if not instance_ids and os.environ.get('INSTANCE_IDS'):
        instance_ids = [id.strip() for id in os.environ.get('INSTANCE_IDS').split(',')]
    
    if not instance_ids:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'No instance IDs provided. Use instance_id, instance_ids, or INSTANCE_IDS environment variable'
            })
        }
    
    # Remove duplicates while preserving order
    instance_ids = list(dict.fromkeys(instance_ids))
    
    # Results tracking
    results = {
        'total_requested': len(instance_ids),
        'successful': [],
        'failed': [],
        'blocked': [],
        'summary': {}
    }
    
    # First, get current state of all instances
    try:
        describe_response = ec2.describe_instances(InstanceIds=instance_ids)
        instance_details = {}
        
        for reservation in describe_response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_details[instance_id] = {
                    'state': instance['State']['Name'],
                    'instance_type': instance['InstanceType'],
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
    except ec2.exceptions.ClientError as e:
        # Some instances might not exist
        instance_details = {}
    
    # Attempt to terminate each instance
    for instance_id in instance_ids:
        try:
            # Check if instance exists and get its current state
            current_info = instance_details.get(instance_id, {})
            current_state = current_info.get('state', 'unknown')
            
            # Check for termination protection or restricted states
            if current_state in ['terminated', 'terminating']:
                results['blocked'].append({
                    'instance_id': instance_id,
                    'reason': f'Instance already in {current_state} state',
                    'current_state': current_state,
                    'details': current_info
                })
                continue
            
            # Attempt termination
            response = ec2.terminate_instances(InstanceIds=[instance_id])
            
            terminating_info = response['TerminatingInstances'][0]
            
            results['successful'].append({
                'instance_id': instance_id,
                'previous_state': terminating_info['PreviousState']['Name'],
                'current_state': terminating_info['CurrentState']['Name'],
                'details': current_info
            })
            
        except ec2.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            # Categorize the error
            blocked_reason = None
            if 'OperationNotPermitted' in error_code:
                blocked_reason = 'Termination protection enabled or insufficient permissions'
            elif 'InvalidInstanceID.NotFound' in error_code:
                blocked_reason = 'Instance does not exist'
            elif 'UnauthorizedOperation' in error_code:
                blocked_reason = 'Insufficient IAM permissions'
            else:
                blocked_reason = error_message
            
            results['blocked'].append({
                'instance_id': instance_id,
                'reason': blocked_reason,
                'error_code': error_code,
                'error_message': error_message,
                'details': current_info
            })
            
        except Exception as e:
            results['failed'].append({
                'instance_id': instance_id,
                'reason': f'Unexpected error: {str(e)}',
                'details': current_info
            })
    
    # Generate summary
    results['summary'] = {
        'total_requested': results['total_requested'],
        'successful_terminations': len(results['successful']),
        'blocked_terminations': len(results['blocked']),
        'failed_terminations': len(results['failed'])
    }
    
    # Determine overall status code
    if results['successful'] and not results['blocked'] and not results['failed']:
        status_code = 200  # All successful
    elif results['successful']:
        status_code = 207  # Partial success
    else:
        status_code = 400  # All failed or blocked
    
    return {
        'statusCode': status_code,
        'body': json.dumps(results, indent=2, default=str)
    }
