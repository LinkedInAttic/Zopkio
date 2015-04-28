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

import zopkio.adhoc_deployer as adhoc_deployer
import zopkio.runtime as runtime

zookeper_deployer = None


def setup_suite():
  print "Starting zookeeper"
  global zookeper_deployer
  env_dict = {}

  if "localhost" not in runtime.get_active_config('zookeeper_host'):
    env_dict = {'JAVA_HOME':'/export/apps/jdk/current'}

  zookeper_deployer = adhoc_deployer.SSHDeployer("zookeeper",
      {'pid_keyword': "zookeeper",
       'executable': runtime.get_active_config('zookeeper_exec_location'),
       'env':env_dict,
       'extract': True,
       'post_install_cmds':runtime.get_active_config('zookeeper_post_install_cmds'),
       'stop_command':runtime.get_active_config('zookeeper_stop_command'),
       'start_command': runtime.get_active_config('zookeeper_start_command')})
  runtime.set_deployer("zookeeper", zookeper_deployer)

  zookeper_deployer.install("zookeeper",
      {"hostname": runtime.get_active_config('zookeeper_host'),
       "install_path": "/tmp/zookeeper_test"})
  zookeper_deployer.start("zookeeper",configs={"sync": True})


def teardown_suite():
   #Terminate Zookeeper
  global zookeper_deployer 
  zookeper_deployer.undeploy("zookeeper")
  print "zookeeper terminated"
