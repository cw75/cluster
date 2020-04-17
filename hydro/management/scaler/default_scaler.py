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

import logging
import random

from hydro.management.util import (
    get_executor_pin_address,
    get_executor_unpin_address,
    send_message
)
from hydro.management.scaler.base_scaler import BaseScaler


class DefaultScaler(BaseScaler):
    def __init__(self, ip, ctx, add_socket, remove_socket, pin_accept_socket):
        self.ip = ip
        self.context = ctx
        self.add_socket = add_socket
        self.remove_socket = remove_socket
        self.pin_accept_socket = pin_accept_socket

    def replicate_function(self, fname, num_replicas, function_locations,
                           executors):
        if num_replicas < 0:
            return

        for _ in range(num_replicas):
            existing_replicas = function_locations[fname]
            candiate_nodes = executors.difference(existing_replicas)

            if len(candiate_nodes) == 0:
                continue

            ip, tid = random.sample(candiate_nodes, 1)[0]

            pin_msg = PinFunction()
            pin_msg.name = fname
            pin_msg.response_address = self.ip

            serialized = pin_msg.SerializeToString()

            send_message(self.context, serialized,
                         get_executor_pin_address(ip, tid))

            function_locations[fname].add((ip, tid))

    def dereplicate_function(self, fname, num_replicas, function_locations):
        if num_replicas < 2:
            return

        while len(function_locations[fname]) > num_replicas:
            ip, tid = random.sample(function_locations[fname], 1)[0]
            send_message(self.context, fname,
                         get_executor_unpin_address(ip, tid))

            function_locations[fname].discard((ip, tid))

    def add_vms(self, kind, count):
        msg = kind + ':' + str(count)
        self.add_socket.send_string(msg)

    def remove_vms(self, kind, ip):
        msg = kind + ':' + ip
        self.remove_socket.send_string(msg)
