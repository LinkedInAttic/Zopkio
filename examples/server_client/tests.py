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

import perf
import zopkio.runtime as runtime


def test_basic():
  """
  Trivial interaction between client and server
  """
  client_deployer = runtime.get_deployer("AdditionClient")

  client_deployer.start("client1", configs={"args": "localhost 8000 1".split(), "delay": 3})
  client_deployer.start("client1", configs={"args": "localhost 8001 1 2".split(), "delay": 3})
  client_deployer.start("client1", configs={"args": "localhost 8002 1 2 3".split(), "delay": 3})

  client_deployer.start("client2", configs={"args": "localhost 8000 1".split(), "delay": 3})
  client_deployer.start("client2", configs={"args": "localhost 8001 1 2".split(), "delay": 3})
  client_deployer.start("client2", configs={"args": "localhost 8002 1 2 3".split(), "delay": 3})


def validate_basic():
  """
  Verify the correct sums are received
  """
  with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
    read_data = output.read()
    assert "Received: 1" in read_data, "Did not receive 1 in client1"
    assert "Received: 3" in read_data, "Did not receive 3 in client1"
    assert "Received: 6" in read_data, "Did not receive 6 in client1"

  with open(os.path.join(perf.LOGS_DIRECTORY, "client2-AdditionClient.log")) as output:
    read_data = output.read()
    assert "Received: 1" in read_data, "Did not receive 1 in client2"
    assert "Received: 3" in read_data, "Did not receive 3 in client2"
    assert "Received: 6" in read_data, "Did not receive 6 in client2"


def test_multi_basic():
  """
  Tests single client multiple runs on same server session
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  server_deployer = runtime.get_deployer("AdditionServer")

  server_deployer.hard_bounce("server1")
  for i in range(0, 3):
    client_deployer.start("client1", configs={"args": "localhost 8000 1 2 3 4".split(), "delay": 3})


def validate_multi_basic():
  """
  Verify 10 (1+2+3+4) is received 3 times
  """
  with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
    read_data = output.read()
    assert read_data.count("Received: 10") == 2, "Did not receive 10 in client1 2 times"  # fail on purpose


def test_server_off():
  """
  Tests what happens when trying to connect when the server is off
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  server_deployer = runtime.get_deployer("AdditionServer")

  server_deployer.stop("server1")
  client_deployer.start("client1", configs={"args": "localhost 8000 1 2 3".split(), "delay": 3})


def validate_server_off():
  """
  Verify that the default error message and a connection refused error message was logged
  """
  with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
    read_data = output.read()
    assert "Addition failed" in read_data, "Did not receive 'Addition failed' in client1"
    assert "Connection refused" in read_data, "Did not receive 'Connection refused' in client1"


def test_no_valid_ints():
  """
  Tests sending non-integers to the server
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  client_deployer.start("client1", configs={"args": "localhost 8000 a b 3.14".split(), "delay": 3})


def validate_no_valid_ints():
  """
  Verify 0 is received since no valid integers were sent
  """
  with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
    assert "Received: 0" in output.read(), "Did not receive 0 in client1"
