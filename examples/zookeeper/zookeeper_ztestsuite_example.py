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

from zopkio.ztests import ZTestSuite, ZTest
import zopkio.adhoc_deployer as adhoc_deployer
import zopkio.runtime as runtime


class ZooKeeperSuite(ZTestSuite):
  def __init__(self, config_dir):
    self.config_dir = config_dir
    self.LOGS_DIRECTORY = "/tmp/zopkio_zookeeper/logs/"
    self.OUTPUT_DIRECTORY = "/tmp/zopkio_zookeeper/results/"
    self.test1 = TestProcessTracking()


  def setup_suite(self):
    print "Starting zookeeper"
    env_dict = {}

    if "localhost" not in runtime.get_active_config('zookeeper_host'):
      env_dict = {'JAVA_HOME':'/export/apps/jdk/current'}

    zookeeper_deployer = adhoc_deployer.SSHDeployer("zookeeper",
        {'pid_keyword': "zookeeper",
         'executable': runtime.get_active_config('zookeeper_exec_location'),
         'env':env_dict,
         'extract': True,
         'post_install_cmds':runtime.get_active_config('zookeeper_post_install_cmds'),
         'stop_command':runtime.get_active_config('zookeeper_stop_command'),
         'start_command': runtime.get_active_config('zookeeper_start_command')})
    runtime.set_deployer("zookeeper", zookeeper_deployer)

    zookeeper_deployer.install("zookeeper",
        {"hostname": runtime.get_active_config('zookeeper_host'),
         "install_path": "/tmp/zookeeper_test"})
    zookeeper_deployer.start("zookeeper",configs={"sync": True})

  def teardown_suite(self):
     #Terminate Zookeeper
    zookeeper_deployer = runtime.get_deployer("zookeeper")
    zookeeper_deployer.undeploy("zookeeper")
    print "zookeeper terminated"

  def process_logs(self, servicename):
    """
    Lists the logs to copy for each service
    :param servicename: the service to fetch logs for
    :return: the names of the log files to copy
    """
    if servicename == "zookeeper":
      return [os.path.join("/tmp/zookeeper_test", "zookeeper.out")]
    else:
      return []

  def naarad_config(self):
    """
    This returns the path of the naarad config for use in performance verification
    :return: The path to the naarad config (future versions may support returning a naarad config object if
    the naarad api changes)
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "naarad.cfg")

def zookeeper_ephemeral_node(name):
  zk = KazooClient(hosts=str(runtime.get_active_config('zookeeper_host') + ':2181'))
  zk.start()
  zk.create("/my/zookeeper_test/node1", b"process1 running", ephemeral=True)
  #At 10 validate that ephemeral node exist that is the process is still running
  time.sleep(10)
  assert zk.exists("/my/zookeeper_test/node1"), "process node is not found at 10 s when it is still running"

  time.sleep(20)
  zk.stop()

class TestProcessTracking(ZTest):
  def test(self):
    """
    Tests if process register node correctly with zookeeper and zookeeper deletes it when process terminates
    """
    #Wait for zookeeper to start so that kazoo client can connect correctly
    time.sleep(5)
    #"connecting to esnure /my/zookeeper_test"

    kazoo_connection_url = str(runtime.get_active_config('zookeeper_host') + ':2181')
    zkclient = KazooClient(hosts=kazoo_connection_url)

    zkclient.start()

    zkclient.ensure_path("/my/zookeeper_test")
    #spawn a python multiprocess which creates an ephermeral node
    #once the process ends the node will be deleted.
    p = Process(target=zookeeper_ephemeral_node, args=("process1",))
    p.start()
    zkclient.stop()

  def validate(self):
    """
    Verify if process register node correctly with zookeeper and zookeeper deletes it when process terminates
    """
    zk = KazooClient(hosts=str(runtime.get_active_config('zookeeper_host') + ':2181'))
    zk.start()

    #At 60 validate that process has terminated by looking at the ephemeral node
    time.sleep(60)
    assert not zk.exists("/my/zookeeper_test/node1"), "process node  not found at 60 s when it should have terminated"

    zk.stop()

ztestsuite = ZooKeeperSuite(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/"))
