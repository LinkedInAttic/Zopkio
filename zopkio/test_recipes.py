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

from datetime import datetime
from datetime import time as dtime
from dateutil import parser
import os
import threading
import random
import logging
import time

import zopkio.runtime as runtime

def test_kill_random_deployer_process(deployer_list, deployer_process_dict, deployer_restart_func_dict={}, deployer_verify_recovery_dict={},deployer_timeout_dict={}):
  """
  A test recipe to select a random deployer and kill one of its process.If no process is present in list then all its process will be killed
  :param deployer_list: List of deployer from which we want to select one and kills its process
  :param deployer_process_dict: dictionary with list of process ids per deployer from which we need to kill one randomly.
  :param deployer_restart_func_dict : dictionary with  key as deployer and value as dict of restart commands if any for list of process.
  :param deployer_verify_recovery_dict: dictionary with  key as deployer and value as verify function per process to verify  if the system was restored correctly.
  :param deployer_timeout_dict: dictionary with  key as deployer and value as optional timeout parameter in seconds per process specified has dictionary.
  """
  if (deployer_list is None):
    assert " No deployer specified in test_kill_random_deployer_process"

  kill_deployer = random.choice(deployer_list)

  kill_deployer_processes = deployer_process_dict.get(kill_deployer,kill_deployer.get_processes())

  test_kill_recovery(kill_deployer, kill_deployer_processes, deployer_restart_func_dict.get(kill_deployer, {}),
                     deployer_verify_recovery_dict.get(kill_deployer, {}), deployer_timeout_dict.get(kill_deployer, {}))


def test_kill_recovery(kill_deployer, kill_deployer_processes, restart_func_dict={}, verify_recovery_dict={}, timeout_dict={}):
  """
  A test recipe to kill a component in distributed system and verify system recovery once its brought back.
  :param kill_deployer: The deployer one of whose process needs to be killed
  :param kill_deployer_processes: list of process ids from which we need to kill one randomly.
  :param restart_func_dict : dictionary with restart commands if any for list of process.
  :param verify_recovery_dict: Verify function per process to verify  if the system was restored correctly.Wait till this function returns true
  :param timeout_dict: optional timeout parameter in seconds per process specified has dictionary. If the system did not recover within this time then error out
  """
  if (kill_deployer is None):
    assert "test_kill_recovery called without any deployer"

  if (kill_deployer_processes is None):
    assert "No process specified for the deployer"

  #stop the deployer's chosen process
  if isinstance(kill_deployer_processes, list):
    kill_process_id = random.choice(kill_deployer_processes)
  else:
    kill_process_id = kill_deployer_processes
  kill_deployer.stop(kill_process_id)


  #Manually restart the process with configs
  if (kill_process_id in restart_func_dict):
    kill_deployer.start(kill_process_id,restart_func_dict[kill_process_id])
  else:
    assert "Restart command not specified for" + kill_process_id

  #verify if the processes has recovered
  if (kill_process_id in verify_recovery_dict):
    start_time = time.time()
    while(not verify_recovery_dict[kill_process_id]()):
      #check for timeout
      if (kill_process_id in timeout_dict):
        assert ((time.time() - start_time) > timeout_dict[kill_process_id]), "Timeout:Killed Process" + kill_process_id + " did not recover correctly"
          




