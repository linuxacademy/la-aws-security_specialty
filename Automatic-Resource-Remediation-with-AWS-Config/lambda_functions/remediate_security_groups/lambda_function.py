"""
Lambda function to poll Config for noncompliant resources, and automatically
apply remediation by replacing the 0.0.0.0/0 22/tcp inbound rule with
10.10.0.0/16 22/tcp. Notifications are sent to an SNS topic.
"""

import boto3

# AWS Config settings
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']
CONFIG_CLIENT = boto3.client('config')
MY_RULE = "restricted-ssh"

# EC2 Settings
EC2_CLIENT = boto3.client('ec2')

# AWS SNS Settings
SNS_CLIENT = boto3.client('sns')
SNS_TOPIC = 'arn:aws:sns:us-east-1:' + ACCOUNT_ID + ':' + 'mytopic'
SNS_SUBJECT = 'Compliance Update'


def lambda_handler(event, context):
    """Entry point"""

    # Get compliance details
    non_compliant_detail = CONFIG_CLIENT.get_compliance_details_by_config_rule(
        ConfigRuleName=MY_RULE, ComplianceTypes=['NON_COMPLIANT'])

    if len(non_compliant_detail['EvaluationResults']) > 0:
        print(
            'The following resource(s) are not compliant with AWS Config rule: '
            + MY_RULE)
        non_complaint_resources = ''
        for result in non_compliant_detail['EvaluationResults']:
            print(result['EvaluationResultIdentifier']
                  ['EvaluationResultQualifier']['ResourceId'])
            non_complaint_resources = non_complaint_resources + \
                result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'] + '\n'

        sns_message = 'AWS Config Compliance Update\n\n Rule: ' \
            + MY_RULE + '\n\n' \
            + 'The following resource(s) are not compliant:\n' \
            + non_complaint_resources

        SNS_CLIENT.publish(TopicArn=SNS_TOPIC,
                           Message=sns_message, Subject=SNS_SUBJECT)

        resource_type = result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceType']

        if resource_type == 'AWS::EC2::SecurityGroup':
            sg_id = result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId']
            sec_group = get_sec_group(sg_id)
            if len(sec_group) > 0:
                vpc_id = sec_group['SecurityGroups'][0]['VpcId']
                remediate_sg('10.10.0.0/16', sg_id, vpc_id)

    else:
        print('No noncompliant resources detected.')


def get_sec_group(sg_id):
    """Return the Security Group given a Security Group ID"""
    sec_group = EC2_CLIENT.describe_security_groups(Filters=[{'Name': 'group-id', 'Values': [sg_id]}])
    return sec_group


def remediate_sg(ip, sg, vpc):
    """Return EC2 SG object based on filters defined by provided VPCID/SGID"""
    sgrules = EC2_CLIENT.describe_security_groups(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [vpc]
        },
        {
            'Name': 'group-id',
            'Values': [sg]
        }
    ]
    )
    r = remove_old_rule(sgrules, sg, ip)
    if r is True:
        sg_add_ingress(ip, sg)
        return True
    elif r is False:
        return False


def remove_old_rule(r, sg, ip):
    """Remove any existing rules in the SG provided the current CIDR doesn't match"""
    rules = r['SecurityGroups'][0]
    if len(rules['IpPermissions']) > 0:
        curr_ip = r['SecurityGroups'][0]['IpPermissions'][0]['IpRanges'][0]['CidrIp']
        if str(ip) == str(curr_ip):
            print('Public IP already exists')
            return False
        else:
            EC2_CLIENT.revoke_security_group_ingress(GroupId=sg, IpPermissions=rules['IpPermissions'])
            return True

    else:
        print('No security group rules for ' + sg)
        return True


def sg_add_ingress(pub_ip, sg):
    """Add ingress rule for SSH TCP/22 to the designated SG"""
    response = EC2_CLIENT.authorize_security_group_ingress(
        GroupId=sg,
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        CidrIp=pub_ip
    )
    return response
