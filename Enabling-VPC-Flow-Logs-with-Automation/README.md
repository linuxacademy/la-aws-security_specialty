# Enabling VPC Flow Logs with Automation

- `lambda_function.py` creates VPC Flow Logs for the VPC ID in the event
- `event-pattern.json` is the CloudWatch Rule event pattern for monitoring the `CreateVpc` API call.
- `test-event.json` is a sample CloudTrail event that can be used with the Lambda function, as it contains the VPC ID