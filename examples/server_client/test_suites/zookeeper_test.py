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
from kazoo.client import KazooClient
from multiprocessing import Process
import time


import perf
import zopkio.runtime as runtime
import zopkio.test_utils as testutilities
import zopkio.adhoc_deployer as adhoc_deployer


zookeper_deployer = None

def start_zookeeper():
  print "Starting zookeeper"
  zookeeper_exec_location = "http://apache.mirrors.pair.com/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz"

  global zookeper_deployer
  zookeper_deployer = adhoc_deployer.SSHDeployer("zookeeper",
      {'pid_keyword': "zookeeper",
       'executable': zookeeper_exec_location,
       'extract': True,
       'post_install_cmds':runtime.get_active_config('zookeeper_post_install_cmds'),
       'stop_command':runtime.get_active_config('zookeeper_stop_command'),
       'start_command': runtime.get_active_config('zookeeper_start_command')})
  runtime.set_deployer("zookeeper", zookeper_deployer)

  zookeper_deployer.install("zookeeper",
      {"hostname": "localhost",
       "install_path": "/tmp/zookeeper_test"})
  zookeper_deployer.start("zookeeper",configs={"sync": True})
  
  #WAit for zookeeper to start so that kazoo client can connect correctly
  time.sleep(5)

def zookeeper_ephemeral_node(name):
  zk = KazooClient(hosts='127.0.0.1:2181')
  zk.start()

  #Create an ephemeral node which will be delete in 30 s
  zk.create("/my/zookeeper_test/node1", b"process1 running", ephemeral=True) 
  time.sleep(30)
  zk.stop()

def test_zookeeper_process_tracking():
  """
  Tests if process register node correctly with zookeeper and zookeeper deletes it when process terminates
  """
  start_zookeeper()

  # create a ZkClient and ensure zookeper_test node
  zkclient = KazooClient(hosts='127.0.0.1:2181')
  zkclient.start()
  zkclient.ensure_path("/my/zookeeper_test")

  #spawn a python multiprocess which creates an ephermeral node
  #once the process ends the node will be deleted.
  p = Process(target=zookeeper_ephemeral_node, args=("process1",))
  p.start()

  zkclient.stop()

def validate_zookeeper_process_tracking():
  """
  Verify if process register node correctly with zookeeper and zookeeper deletes it when process terminates
  """

  time.sleep(10)
  zk = KazooClient(hosts='127.0.0.1:2181')
  zk.start()

  #At 10 validate that ephemeral node exist that is the process is still running
  assert zk.exists("/my/zookeeper_test/node1"), "process node is not found at 10 s when it is still running"
  
  #At 60 validate that process has terminated by looking at the ephemeral node
  time.sleep(50)
  assert not zk.exists("/my/zookeeper_test/node1"), "process node  not found at 60 s when it should have terminated"

  #Terminate Zookeeper
  zookeper_deployer.undeploy("zookeeper")
  print "zookeeper terminated"

  zk.stop()


