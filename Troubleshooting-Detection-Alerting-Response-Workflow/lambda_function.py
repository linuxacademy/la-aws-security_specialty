import boto3
import json


def lambda_handler(event, context):
    '''
    Extract the EC2 instance ID from the Alarm Description, and stop the
    instance.
    '''

    try:
        json_message = event['Message']
        message = json.loads(json_message)
        instance = message['AlarmDescription'].split()[-1]

        print("Instance: " + instance)

        ec2 = boto3.client('ec2')
        ec2.stop_instances(InstanceIds=[instance])

        print('Stopped instance: ' + instance)
    except Exception as e:
        print('Error: ' + e)
