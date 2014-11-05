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

import zopkio.adhoc_deployer as adhoc_deployer
import zopkio.runtime as runtime

server_deployer = None
client_deployer = None


def setup_suite():
  client_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)),
      "AdditionClient/out/artifacts/AdditionClient_jar/AdditionClient.jar")
  global client_deployer
  client_deployer = adhoc_deployer.SSHDeployer("AdditionClient",
      {'pid_keyword': "AdditionClient",
       'executable': client_exec,
       'start_command': "java -jar AdditionClient.jar"})
  runtime.set_deployer("AdditionClient", client_deployer)

  client_deployer.install("client1",
      {"hostname": "localhost",
       "install_path": "/tmp/server_client/AdditionClients/client1"})

  client_deployer.install("client2",
      {"hostname": "localhost",
       "install_path": "/tmp/server_client/AdditionClients/client2"})

  server_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)),
      "AdditionServer/out/artifacts/AdditionServer_jar/AdditionServer.jar")
  global server_deployer
  server_deployer = adhoc_deployer.SSHDeployer("AdditionServer",
      {'pid_keyword': "AdditionServer",
       'executable': server_exec,
       'start_command': "java -jar AdditionServer.jar"})
  runtime.set_deployer("AdditionServer", server_deployer)

  server_deployer.deploy("server1",
      {"hostname": "localhost",
       "install_path": "/tmp/server_client/AdditionServers/server1",
       "args": "localhost 8000".split()})

  server_deployer.deploy("server2",
      {"hostname": "localhost",
       "install_path": "/tmp/server_client/AdditionServers/server2",
       "args": "localhost 8001".split()})

  server_deployer.deploy("server3",
      {"hostname": "localhost",
       "install_path": "/tmp/server_client/AdditionServers/server3",
       "args": "localhost 8002".split()})

def setup():
  for process in server_deployer.get_processes():
    server_deployer.start(process.unique_id)

def teardown():
  for process in client_deployer.get_processes():
    client_deployer.stop(process.unique_id)

def teardown_suite():
  for process in server_deployer.get_processes():
    server_deployer.undeploy(process.unique_id)
