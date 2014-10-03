# Copyright 2014 LinkedIn Corp.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os

LOGS_DIRECTORY = "/tmp/server_client_test/collected_logs/"
OUTPUT_DIRECTORY = "/tmp/server_client_test/results/"

def machine_logs():
  return {
    "server1": [os.path.join("/tmp/server_client/AdditionServers/server1", "logs/AdditionServer.log")],
    "server2": [os.path.join("/tmp/server_client/AdditionServers/server2", "logs/AdditionServer.log")],
    "server3": [os.path.join("/tmp/server_client/AdditionServers/server3", "logs/AdditionServer.log")],

    "client1": [os.path.join("/tmp/server_client/AdditionClients/client1", "logs/AdditionClient.log")],
    "client2": [os.path.join("/tmp/server_client/AdditionClients/client2", "logs/AdditionClient.log")],
  }

def naarad_logs():
  return {
    "server1": [os.path.join("/tmp/server_client/AdditionServers/server1", "logs/AdditionServerPerf.csv")],
    "server2": [os.path.join("/tmp/server_client/AdditionServers/server2", "logs/AdditionServerPerf.csv")],
    "server3": [os.path.join("/tmp/server_client/AdditionServers/server3", "logs/AdditionServerPerf.csv")],

    "client1": [os.path.join("/tmp/server_client/AdditionClients/client1", "logs/AdditionClientPerf.csv")],
    "client2": [os.path.join("/tmp/server_client/AdditionClients/client2", "logs/AdditionClientPerf.csv")],
  }


def naarad_config(config, test_name=None):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), "naarad.cfg")
