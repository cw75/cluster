#!/bin/bash

kubectl drain $1 --ignore-daemonsets --delete-local-data > /dev/null 2>&1

YML_FILE=yaml/igs/$2-ig.yml

sed "s|CLUSTER_NAME|$HYDRO_CLUSTER_NAME|g" $YML_FILE > tmp.yml
sed -i "s|NUM_DUMMY|$3|g" tmp.yml

kops replace -f tmp.yml --force > /dev/null 2>&1
rm tmp.yml

kubectl delete node $1 > /dev/null 2>&1

kops update cluster --name ${HYDRO_CLUSTER_NAME} --yes > /dev/null 2>&1
#ID=$(aws ec2 --region us-east-1 describe-instances --filter Name=private-dns-name,Values=$1 --query 'Reservations[].Instances[].InstanceId' --output text)
#aws ec2 --region us-east-1 terminate-instances --instance-ids $ID > /dev/null 2>&1