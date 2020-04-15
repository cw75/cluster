#!/bin/bash

kubectl drain $1 > /dev/null 2>&1

kubectl delete node $1 > /dev/null 2>&1

ID=$(aws ec2 describe-instances --filter Name=private-dns-name,Values=$1 --query 'Reservations[].Instances[].InstanceId' --output text)
aws ec2 terminate-instances --instance-ids $ID > /dev/null 2>&1