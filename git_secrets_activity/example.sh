#!/usr/bin/env bash

AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY = 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

echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"

aws ec2 describe-vpcs --query "Vpcs[].CidrBlock"

roles=$(aws iam list-roles --query 'Roles[?starts_with(RoleName, `aws`)].RoleName' --output json)

echo roles $roles

aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' \
    --filters Name=instance-state-name,Values=running --output text
aws s3 ls
aws apigateway get-rest-apis

aws ec2 create-image --instance-id i-00000000 --name "Dev AMI" --description "AMI for development server"
