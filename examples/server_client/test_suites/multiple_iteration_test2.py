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


test_phase = 2


def test_negative_correctness():
  """
  Tests sending non-integers to the server
  """
  #Leaving the print for proof of order  
  print "test_negative_correctness"
  client_deployer = runtime.get_deployer("AdditionClient")
  client_deployer.start("client1", configs={"args": "localhost 8000 a b 3.14".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8000 a b 3.14".split(), "sync": True})


def validate_negative_correctness():
  """
  Verify 0 is received since no valid integers were sent
  """
  print "validate_negative_correctness"
  client1_log_file = os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")
  client1_logs = testutilities.get_log_for_test("test_negative_correctness", client1_log_file, "12:00:00")
  assert "Received: 0" in client1_logs, "Did not receive 0 in client1"



