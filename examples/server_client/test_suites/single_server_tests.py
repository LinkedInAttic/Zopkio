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
import threading

import perf
import zopkio.runtime as runtime
import zopkio.test_utils as testutilities

SAMPLE = lambda size: [str(i) for i in range(1, size + 1)]
SMALL_SAMPLE = SAMPLE(3)
MEDIUM_SAMPLE = SAMPLE(100)
LARGE_SAMPLE = SAMPLE(1000)


def test_redlining():
  """
  Sends a large sample of integers to the server.
  """
  # obtain the deployer for AdditionClient
  client_deployer = runtime.get_deployer("AdditionClient")

  # set client to connect to localhost:8000 with a large sample
  client_deployer.start("client1", configs={"args": "localhost 8000".split() + LARGE_SAMPLE, "sync": True})


def validate_redlining():
  """
  Verify max latency of server is <0.5 sec
  """
  metrics = runtime.get_active_test_metrics("test_redlining")
  assert metrics["server1-perf"]["latency"]["max"] < 0.5, "server latency too high while sending 10000 integers"


def test_ordered_events():
  """
  Tests that integers to a server are received in the same order that they are sent
  """
  client_deployer = runtime.get_deployer("AdditionClient")

  # set client to connect to localhost:8000 and send 1, 2, and 3 in that order
  client_deployer.start("client1", configs={"args": "localhost 8000 1 2 3".split(), "sync": True})


def validate_ordered_events():
  """
  Validates that the integers 1, 2, and 3, were sent in that specific order
  """
  # keep track of which number has been read
  state = 0

  server1_log_file = os.path.join(perf.LOGS_DIRECTORY, "server1-AdditionServer.log")
  server1_logs = testutilities.get_log_for_test("test_ordered_events", server1_log_file, "12:00:00")
  # verify that 1, 2, 3 were received by the server in order
  for line in server1_logs.split('\n'):
    if "Received 1" in line:
      state = 1
    if "Received 2" in line:
      if state == 1:
        state = 2
      else:
        break
    if "Received 3" in line:
      if state == 2:
        state = 3
        break
      else:
        break
  assert state == 3, "Integers 1, 2, 3 were not received in the correct order"


def test_bouncing_with_state():
  """
  Tests that bouncing the server retains state
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  server_deployer = runtime.get_deployer("AdditionServer")

  start_client = lambda: client_deployer.start("client1", configs={"args": "localhost 8000".split() + LARGE_SAMPLE, "sync": True})
  client_thread = threading.Thread(target=start_client)

  # create a thread that will bounce (stop and start) the server
  bounce_server = lambda: server_deployer.soft_bounce("server1")
  server_thread = threading.Thread(target=bounce_server)

  client_thread.start()
  server_thread.start()
  client_thread.join()


def validate_bouncing_with_state():
  """
  Verify that the sum 500,500 is received
  """
  client1_log_file = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client1_logs = testutilities.get_log_for_test("test_bouncing_with_state", client1_log_file, "12:00:00")
  assert "Received: 5050" in client1_logs, "Did not received 5050 in client1"
