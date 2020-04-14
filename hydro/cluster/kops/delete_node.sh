#!/bin/bash

kubectl drain $1 --ignore-daemonsets --delete-local-data

kubectl delete node $1