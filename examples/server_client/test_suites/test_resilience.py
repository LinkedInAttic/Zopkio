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
import zopkio.test_recipes as testrecipe

tests_iteration = 1

def verify_client_recovery():
  return True


def test_resilience():
  """
  Tests if after killing one of the clients it restarts back correctly within 10 seconds
  """
  client_deployer = runtime.get_deployer("AdditionClient")

  client_deployer.start("client1", configs={"args": "localhost 8000 1".split(), "sync": True})
  client_deployer.start("client2", configs={"args": "localhost 8002 1 2 3".split(), "sync": True})

  restart_func_dict = {"client1":{"args": "localhost 8000 1".split(), "sync": True}, "client2" : {"args": "localhost 8002 1 2 3".split(), "sync": True}}

  verify_client_recovery_dict = {"client1" : verify_client_recovery, "client2" : verify_client_recovery}

  timeout_dict = {"client1" : 10, "client2" : 10}
  
  #Verifies if the client recovers in 10s
  testrecipe.test_kill_recovery(client_deployer, ["client1", "client2"], restart_func_dict, verify_client_recovery_dict, timeout_dict)
