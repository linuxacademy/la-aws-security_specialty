import boto3
import json


def lambda_handler(event, context):
    '''
    Extract the EC2 instance ID from the Alarm Description, and stop the
    instance.
    '''

    try:
        print(event)
        sns = event['Records'][0]['Sns']
        print('DEBUG:', sns['Message'])
        json_msg = json.loads(sns['Message'])
        instance = json_msg['AlarmDescription'].split()[-1]

        print("Instance: " + instance)

        ec2 = boto3.client('ec2')
        ec2.stop_instances(InstanceIds=[instance])

        print('Stopped instance: %s' % instance)

    except Exception as e:
        print('Error - reason "%s"' % str(e))
