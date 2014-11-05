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
import zopkio.test_utils as testutilities


SAMPLE = lambda size: [str(i) for i in range(1, size + 1)]
SMALL_SAMPLE = SAMPLE(3)
MEDIUM_SAMPLE = SAMPLE(100)
LARGE_SAMPLE = SAMPLE(1000)


def test_load_balance():
  """
  Tests if clients perform correct load balancing
  """
  client_deployer = runtime.get_deployer("AdditionClient")

  # start the client that will send integers from 1 to 1000
  for i in range(3):
    client_deployer.start("client1", configs={"args": "localhost 8000".split() + SMALL_SAMPLE, "sync": True})


def validate_load_balance():
  """
  Verify that one server did not process all requests
  """
  server1_log_file = os.path.join(perf.LOGS_DIRECTORY, "server1-AdditionServer.log")
  server1_logs = testutilities.get_log_for_test("test_load_balance", server1_log_file, "12:00:00")
  assert "Responding with 6" in server1_logs != 3, "One server processed all requests"


def test_fault_tolerance():
  """
  Tests what happens when servers are stopped
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  server_deployer = runtime.get_deployer("AdditionServer")

  server_deployer.stop("server2")
  server_deployer.stop("server3")

  client_deployer.start("client1", configs={"args": "localhost 8000".split() + SMALL_SAMPLE, "sync": True})


def validate_fault_tolerance():
  """
  Verify that 10 is received
  """
  client1_log_file = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client1_logs = testutilities.get_log_for_test("test_fault_tolerance", client1_log_file, "12:00:00")
  assert "Received: 6" in client1_logs, "Server did not pass fault tolerance"


def test_race_condition():
  """
  Tests what happens when two clients send requests to the same server
  """
  # obtain the deployer for AdditionClients
  client_deployer = runtime.get_deployer("AdditionClient")

  start_client1 = lambda: client_deployer.start("client1", configs={"args": "localhost 8000".split() + SMALL_SAMPLE, "sync": True})
  start_client2 = lambda: client_deployer.start("client2", configs={"args": "localhost 8000".split() + SMALL_SAMPLE, "sync": True})
  testutilities.start_threads_and_join([start_client1, start_client2])


def validate_race_condition():
  server1_log_file = os.path.join(perf.LOGS_DIRECTORY, "server1-AdditionServer.log")
  server1_logs = testutilities.get_log_for_test("test_race_condition", server1_log_file, "12:00:00")
  assert "Responding with 6" in server1_logs == 3, "Race condition fail"
