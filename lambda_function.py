import boto3
import json
import os

def lambda_handler(event, context):
    """
    Lambda function to terminate an EC2 instance.
    
    Environment Variables:
        INSTANCE_ID: The ID of the instance to terminate (optional, can be passed in event)
    
    Event Parameters:
        instance_id: The ID of the instance to terminate (overrides environment variable)
    
    Returns:
        dict: Response with status code and message
    """
    
    # Initialize EC2 client
    ec2 = boto3.client('ec2')
    
    # Get instance ID from event or environment variable
    instance_id = event.get('instance_id') or os.environ.get('INSTANCE_ID')
    
    if not instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'No instance_id provided in event or INSTANCE_ID environment variable'
            })
        }
    
    try:
        # Terminate the instance
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        
        # Get the current state of the instance
        current_state = response['TerminatingInstances'][0]['CurrentState']['Name']
        previous_state = response['TerminatingInstances'][0]['PreviousState']['Name']
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully initiated termination of instance {instance_id}',
                'instance_id': instance_id,
                'previous_state': previous_state,
                'current_state': current_state
            })
        }
        
    except ec2.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'{error_code}: {error_message}',
                'instance_id': instance_id
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Unexpected error: {str(e)}',
                'instance_id': instance_id
            })
        }
