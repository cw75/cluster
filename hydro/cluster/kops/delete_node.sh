#!/bin/bash

kubectl drain $1 --ignore-daemonsets --delete-local-data > /dev/null 2>&1

kubectl delete node $1 > /dev/null 2>&1