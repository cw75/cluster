#!/usr/bin/env python3

#  Copyright 2019 U.C. Berkeley RISE Lab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import os

import boto3

from hydro.cluster.add_nodes import batch_add_nodes
from hydro.shared import util

BATCH_SIZE = 400

ec2_client = boto3.client('ec2', os.getenv('AWS_REGION', 'us-east-1'))

def create_cluster(server_count, ssh_key, cluster_name, kops_bucket,
                   aws_key_id, aws_key):

    if 'HYDRO_HOME' not in os.environ:
        raise ValueError('HYDRO_HOME environment variable must be set to be '
                         + 'the directory where all Hydro project repos are '
                         + 'located.')
    prefix = os.path.join(os.environ['HYDRO_HOME'], 'cluster/hydro/cluster')

    util.run_process(['./create_cluster_object.sh', kops_bucket, ssh_key])

    client, apps_client = util.init_k8s()

    print('Creating %d server nodes...' % (server_count))
    batch_add_nodes(client, apps_client, ['server'], [server_count], BATCH_SIZE, prefix, aws_key_id, aws_key)

    print('Finished creating all pods...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Creates a Hydro cluster
                                     using Kubernetes and kops. If no SSH key
                                     is specified, we use the default SSH key
                                     (~/.ssh/id_rsa), and we expect that the
                                     correponding public key has the same path
                                     and ends in .pub.

                                     If no configuration file base is
                                     specified, we use the default
                                     ($HYDRO_HOME/anna/conf/anna-base.yml).''')

    parser.add_argument('-s', '--server', nargs=1, type=int, metavar='S',
                        help='The number of server nodes ' +
                        '(required)', dest='server', required=True)
    parser.add_argument('--ssh-key', nargs='?', type=str,
                        help='The SSH key used to configure and connect to ' +
                        'each node (optional)', dest='sshkey',
                        default=os.path.join(os.environ['HOME'],
                                             '.ssh/id_rsa'))

    cluster_name = util.check_or_get_env_arg('HYDRO_CLUSTER_NAME')
    kops_bucket = util.check_or_get_env_arg('KOPS_STATE_STORE')
    aws_key_id = util.check_or_get_env_arg('AWS_ACCESS_KEY_ID')
    aws_key = util.check_or_get_env_arg('AWS_SECRET_ACCESS_KEY')

    args = parser.parse_args()

    create_cluster(args.server[0], args.sshkey, cluster_name, kops_bucket, aws_key_id, aws_key)