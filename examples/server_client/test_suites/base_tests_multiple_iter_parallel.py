# Copyright 2015 LinkedIn Corp.
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
import time

import perf
import zopkio.runtime as runtime
import zopkio.test_utils as testutilities

def create_sample(n):
    sample_list = []
    for i in xrange(1,n+1):
        sample_list.append(i)
    return sample_list

SMALL_SAMPLE = create_sample(3)
MEDIUM_SAMPLE = create_sample(100)
LARGE_SAMPLE = create_sample(1000)
tests_iteration = 3
test_phase = 1


def test_correctness():
  """
  Tests if the correct sums are calculated
  """
  client_deployer = runtime.get_deployer("AdditionClient")

  client_deployer.start("client1", configs={"args": "localhost 8000 1".split(), "sync": True})
  client_deployer.start("client1", configs={"args": "localhost 8001 1 2".split(), "sync": True})
  client_deployer.start("client1", configs={"args": "localhost 8002 1 2 3".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8000 1".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8001 1 2".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8002 1 2 3".split(), "sync": True})


def validate_correctness():
  """
  Verify the correct sums are received
  """
  client1_log_file = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client1_logs = testutilities.get_log_for_test("test_correctness", client1_log_file, "12:00:00")
  assert "Received: 1" in client1_logs, "Did not receive 1 in client1"
  assert "Received: 3" in client1_logs, "Did not receive 3 in client1"
  assert "Received: 6" in client1_logs, "Did not receive 6 in client1"

  client2_log = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client2_logs = testutilities.get_log_for_test("test_correctness", client2_log, "12:00:00")
  assert "Received: 1" in client2_logs, "Did not receive 1 in client2"
  assert "Received: 3" in client2_logs, "Did not receive 3 in client2"
  assert "Received: 6" in client2_logs, "Did not receive 6 in client2"


def test_negative_correctness():
  """
  Tests sending non-integers to the server
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  client_deployer.start("client1", configs={"args": "localhost 8000 a b 3.14".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8000 a b 3.14".split(), "sync": True})


def validate_negative_correctness():
  """
  Verify 0 is received since no valid integers were sent
  """
  client1_log_file = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client1_logs = testutilities.get_log_for_test("test_negative_correctness", client1_log_file, "12:00:00")
  assert "Received: 0" in client1_logs, "Did not receive 0 in client1"


def test_single_client_perf():
  """
  Tests the performance of a server when handling single client
  """
  client_deployer = runtime.get_deployer("AdditionClient")
  client_deployer.start("client1", configs={"args": "localhost 8000".split() + MEDIUM_SAMPLE, "sync": True})


def validate_single_client_perf():
  """
  Validate server max qps is >100 and mean latency is <0.2 sec
  """
  metrics = runtime.get_active_test_metrics("test_single_client_perf")
  assert metrics["server1-perf"]["qps"]["max"] > 100, "qps too low"
  assert metrics["server1-perf"]["latency"]["max"] < 0.2, "latency too high"

