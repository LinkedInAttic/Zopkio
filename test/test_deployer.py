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
import shutil
import unittest

from zopkio.deployer import Deployer, Process
from zopkio.remote_host_helper import ParamikoError, better_exec_command, get_ssh_client, copy_dir, get_sftp_client
from .mock import Mock_Deployer

class TestDeployer(unittest.TestCase):



  def test_better_exec(self):
    """
    Tests that the better_exec in the deployer module works and detects failed
    commands
    """
    with get_ssh_client("127.0.0.1") as ssh:
      better_exec_command(ssh, "true", "This command succeeds")
      self.assertRaises(ParamikoError, better_exec_command, ssh,
                        "false", "This command fails")

  def test_get_logs(self):
    """
    Tests that we can successfully copy logs from a remote host
    :return:
    """
    minimial_deployer = Mock_Deployer()
    install_path = '/tmp/test_deployer_get_logs'
    if not os.path.exists(install_path):
      os.mkdir(install_path)

    output_path = '/tmp/test_deployer_get_logs_output'
    if not os.path.exists(output_path):
      os.mkdir(output_path)
    with open(os.path.join(install_path, 'test.log'), 'w') as f:
      f.write('this is the test log')
    with open(os.path.join(install_path, 'test.out'), 'w') as f:
      f.write('this is the test out')
    with open(os.path.join(install_path, 'test.foo'), 'w') as f:
      f.write('this is the test foo')
    minimial_deployer.processes['unique_id'] = Process('unique_id', 'service_name', 'localhost', install_path)
    minimial_deployer.get_logs('unique_id', [os.path.join(install_path, 'test.out')], output_path, '')
    assert os.path.exists(os.path.join(output_path, "unique_id-test.out"))
    shutil.rmtree(output_path)
    if not os.path.exists(output_path):
      os.mkdir(output_path)
    minimial_deployer.get_logs('unique_id', [], output_path, '.*log')
    assert os.path.exists(os.path.join(output_path, "unique_id_test_deployer_get_logs-test.log"))
    shutil.rmtree(install_path)
    shutil.rmtree(output_path)

  def test_copy_logs(self):

    install_path = '/tmp/test_copy_dir'
    if not os.path.exists(install_path):
      os.mkdir(install_path)

    output_path = '/tmp/test_copy_dir_output'
    if not os.path.exists(output_path):
      os.mkdir(output_path)
    with open(os.path.join(install_path, 'test.log'), 'w') as f:
      f.write('this is the test log')
    with open(os.path.join(install_path, 'test.out'), 'w') as f:
      f.write('this is the test out')
    with open(os.path.join(install_path, 'test.foo'), 'w') as f:
      f.write('this is the test foo')
    with get_sftp_client('localhost') as ftp:
      copy_dir(ftp, install_path, output_path, 'prefix', '.*out')
    assert os.path.exists(os.path.join(output_path, "prefix_test_copy_dir-test.out"))
    shutil.rmtree(output_path)
    shutil.rmtree(install_path)

if __name__ == '__main__':
  unittest.main()
