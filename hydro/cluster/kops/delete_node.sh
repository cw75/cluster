#!/bin/bash

kubectl drain $1 --ignore-daemonsets --delete-local-data > /dev/null 2>&1

kubectl delete node $1 > /dev/null 2>&1

ID=$(aws ec2 --region us-east-1 describe-instances --filter Name=private-dns-name,Values=$1 --query 'Reservations[].Instances[].InstanceId' --output text)
aws ec2 --region us-east-1 terminate-instances --instance-ids $ID > /dev/null 2>&1