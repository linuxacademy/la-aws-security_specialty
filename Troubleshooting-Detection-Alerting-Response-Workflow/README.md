# Troubleshooting a Detection, Alerting, and Response Workflow

Resources for this learning activity:

- `lambda_function.py` - Invoked in response to SNS notification, stopping the EC2 instance
- `sshaccess.conf` - CloudWatch Logs Agent config file
- `sns_event.json` - Sample SNS notification event
- `event_message.json` - Decoded JSON message from within SNS event

More information about CloudWatch Logs Agent config files here: <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AgentReference.html>
