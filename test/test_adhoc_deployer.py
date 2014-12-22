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
import tarfile
import zipfile
import unittest

import zopkio.constants as constants
import zopkio.adhoc_deployer as adhoc_deployer

class TestAdhocDeployer(unittest.TestCase):
  def setUp(self):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    executable = os.path.join(test_dir, "samples/trivial_program")
    install_path = "/tmp/ssh_deployer_test/"
    start_cmd = "chmod a+x trivial_program; ./trivial_program"
    files_to_clean = ["/tmp/trivial_output"]
    self.trivial_deployer = adhoc_deployer.SSHDeployer("sample_program",
        {'executable': executable,
         'install_path': install_path,
         'start_command': start_cmd,
         'directories_to_clean': files_to_clean,
         'terminate_only': True,
         'pid_keyword': 'trivial_program',
         'post_install_cmds': [
           'touch {0}/trivial-post-cmd'.format(install_path)
         ]})

  def test_ssh_deployer_install_uninstall(self):
    """
    Test install and uninstall
    """
    self.trivial_deployer.install("unique_id0", {'hostname': "localhost"})
    self.assertTrue(os.path.isdir("/tmp/ssh_deployer_test/"))
    self.assertTrue(os.path.isfile("/tmp/ssh_deployer_test/trivial_program"))
    self.assertTrue(os.path.isfile("/tmp/ssh_deployer_test/trivial-post-cmd"))
    self.trivial_deployer.uninstall("unique_id0")
    self.assertFalse(os.path.isdir("/tmp/ssh_deployer_test/"))

  def test_ssh_deployer_start_stop(self):
    """
    Test start and stop
    """
    self.trivial_deployer.install("unique_id0", {'hostname': "localhost"})
    self.assertTrue(os.path.isdir("/tmp/ssh_deployer_test/"))
    self.assertTrue(os.path.isfile("/tmp/ssh_deployer_test/trivial_program"))
    self.trivial_deployer.start("unique_id0")
    self.assertNotEqual(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    self.trivial_deployer.stop("unique_id0")
    self.assertEqual(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    self.trivial_deployer.uninstall("unique_id0")
    self.assertFalse(os.path.isdir("/tmp/ssh_deployer_test/"))

  def test_ssh_deployer_deploy_undeploy(self):
    """
    Test deploy and undeploy
    """
    self.trivial_deployer.deploy("unique_id0", {'hostname': "localhost"})
    self.assertTrue(os.path.isdir("/tmp/ssh_deployer_test/"))
    self.assertTrue(os.path.isfile("/tmp/ssh_deployer_test/trivial_program"))
    self.assertNotEqual(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    self.trivial_deployer.undeploy("unique_id0")
    self.assertFalse(os.path.isdir("/tmp/ssh_deployer_test/"))
    self.assertEqual(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)

  def test_ssh_deployer_get_log(self):
    """
    Test get logs
    """
    self.trivial_deployer.deploy("unique_id0", {'hostname': "localhost"})
    self.assertTrue(os.path.isdir("/tmp/ssh_deployer_test/"))
    self.assertTrue(os.path.isfile("/tmp/ssh_deployer_test/trivial_program"))
    self.assertNotEqual(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    if not os.path.isdir("/tmp/trivial_output_while_running"):
      os.makedirs("/tmp/trivial_output_while_running")

    self.trivial_deployer.get_logs("unique_id0", ["/tmp/trivial_output"],
                                   "/tmp/trivial_output_while_running")
    self.trivial_deployer.stop("unique_id0",
                               {'pid_keyword': 'trivial_program'})
    self.assertEquals(
        self.trivial_deployer.get_pid("unique_id0",
                                      {'pid_keyword': 'trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    if not os.path.isdir("/tmp/trivial_output_while_not_running"):
      os.makedirs("/tmp/trivial_output_while_not_running")

    self.trivial_deployer.get_logs("unique_id0", ["/tmp/trivial_output"],
                                   "/tmp/trivial_output_while_not_running")
    self.trivial_deployer.uninstall("unique_id0")
    self.assertFalse(os.path.isdir("/tmp/ssh_deployer_test/"))

  def test_ssh_deployer_get_pid(self):
    """
    Test get_pid
    """
    self.trivial_deployer.deploy("unique_id0", {'hostname': "localhost"})
    #self.trivial_deployer.deploy("unique_id1", {'hostname': "localhost"})
    #self.trivial_deployer.deploy("unique_id2", {'hostname': "localhost"})
    #self.trivial_deployer.deploy("unique_id3", {'hostname': "localhost"})
    #self.trivial_deployer.deploy("unique_id4", {'hostname': "localhost"})
    pids = self.trivial_deployer.get_pid("unique_id0",
                                         {'pid_keyword': 'trivial_program'})
    assert len(pids) > 0
    pid_file = "/tmp/test_ssh_deployer_get_pid_file"
    with open(pid_file, 'w') as f:
      file_str = '\n'.join([str(pid) for pid in pids])
      f.write(file_str)
    assert pids == self.trivial_deployer.get_pid("unique_id0", {'pid_file': pid_file})
    self.trivial_deployer.undeploy("unique_id0")
    assert self.trivial_deployer.get_pid("unique_id0", {'pid_keyword': 'samples/trivial_program'})\
           == constants.PROCESS_NOT_RUNNING_PID
    os.remove(pid_file)
    self.trivial_deployer.undeploy("unique_id0")

  def test_tar_executable(self):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    executable = os.path.join(test_dir, "samples/trivial_program.tar")

    tar = tarfile.open(executable, "w")
    try:
      tar.add(os.path.join(test_dir, "samples/trivial_program"), "samples/trivial_program")
    finally:
      tar.close()

    install_path = "/tmp/tar_test/"
    start_cmd = "chmod a+x samples/trivial_program; ./samples/trivial_program"
    files_to_clean = ["/tmp/trivial_output"]
    tar_deployer = adhoc_deployer.SSHDeployer("samples/trivial_program",
        {'executable': executable,
         'extract': True,
         'install_path': install_path,
         'start_command': start_cmd,
         'directories_to_remove': files_to_clean})
    tar_deployer.deploy("samples/trivial_program", {'hostname': "localhost"})
    self.assertNotEqual(
        tar_deployer.get_pid("samples/trivial_program",
                             {'pid_keyword': 'samples/trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    tar_deployer.undeploy("samples/trivial_program", {'pid_keyword': 'samples/trivial_program'})
    os.remove(executable)

  def test_zip_executable(self):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    executable = os.path.join(test_dir, "samples/trivial_program.zip")

    zf = zipfile.ZipFile(executable, "w")
    try:
      zf.write(os.path.join(test_dir, "samples/trivial_program"), "samples/trivial_program",
               zipfile.ZIP_DEFLATED)
    finally:
      zf.close()
    install_path = "/tmp/zip_test/"
    start_cmd = "chmod a+x samples/trivial_program; ./samples/trivial_program"
    files_to_clean = ["/tmp/trivial_output"]
    zip_deployer = adhoc_deployer.SSHDeployer("samples/trivial_program",
        {'executable': executable,
         'extract': True,
         'install_path': install_path,
         'start_command': start_cmd,
         'directories_to_remove': files_to_clean})
    zip_deployer.deploy("samples/trivial_program", {'hostname': "localhost"})
    self.assertNotEqual(
        zip_deployer.get_pid("samples/trivial_program",
                             {'pid_keyword': 'samples/trivial_program'}),
        constants.PROCESS_NOT_RUNNING_PID)
    zip_deployer.undeploy("samples/trivial_program", {'pid_keyword': 'samples/trivial_program'})
    os.remove(executable)

if __name__ == '__main__':
  unittest.main()
