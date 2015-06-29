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
from kazoo.client import KazooClient
from multiprocessing import Process
import time

import zopkio.runtime as runtime
import zopkio.test_utils as testutilities
import zopkio.adhoc_deployer as adhoc_deployer


zookeper_deployer = None
test_phase = 2

def test_zookeeper_fault_tolerance():
  """
  Kill zookeeper1 and see if other zookeeper instances are in quorum
  """
  zookeper_deployer = runtime.get_deployer("zookeeper")
  kazoo_connection_url = str(runtime.get_active_config('zookeeper_host') + ':2181')
  zkclient = KazooClient(hosts=kazoo_connection_url)

  zkclient.start()

  zkclient.ensure_path("/my/zookeeper_errorinjection")
  # kill the Zookeeper1 instance
  print "killing zoookeeper instance1"
  zookeper_deployer.kill("zookeeper1")
  time.sleep(20)
  zkclient.stop()

def validate_zookeeper_fault_tolerance():
  """
  Validate that we can still connect to zookeeper instance 2 to read the node
  """
  zk2 = KazooClient(hosts=str(runtime.get_active_config('zookeeper_host') + ':2182'))
  zk2.start()
  assert zk2.exists("/my/zookeeper_errorinjection/"), "zookeeper_errorinjection node not found"

  zk2.stop()

