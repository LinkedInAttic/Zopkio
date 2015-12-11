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
import zopkio.remote_host_helper as remote_host_helper
import zopkio.runtime as runtime
from zopkio.ztests import ZTest, ZTestSuite
import shutil
from time import sleep
__test__ = False  # don't this as a test

TEST_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SampleTest0(ZTest):
  phase = 0
  def test(self):
    """
    Yay! Docstring!
    """
    assert 1 == 2

class SampleTest1(ZTest):
  phase = 0

  def __init__(self, sampletestsuite):
    self.sampletestsuite = sampletestsuite

  def test(self):
    self.sampletestsuite.sample_code_in.write("test1\n")
    self.sampletestsuite.sample_code_in.flush()
    sleep(5)
    with open("/tmp/trivial_timed_output", "r") as f:
      lines = f.readlines()
      test_str = "".join(lines)
      assert "test1" in test_str

class SampleTest2(ZTest):
  phase = 1

  def __init__(self, sampletestsuite):
    self.sampletestsuite = sampletestsuite


  def test(self):
    """
    Another docstring
    """
    for i in xrange(50, 150):
      self.sampletestsuite.sample_code_in.write("{0}\n".format(i))
      self.sampletestsuite.sample_code_in.flush()
      sleep(.05)



  def validate(self):
    assert 1 == 1


class SampleTestSuite(ZTestSuite):
  config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ztestsuite_configs")

  def __init__(self, deployer = None):
    self.ssh = remote_host_helper.sshclient()
    self.ssh.load_system_host_keys()
    self.sample_code_in = None
    self.test0 = SampleTest0()
    self.test1 = SampleTest1(self)
    self.test2 = SampleTest2(self)
    self._deployer = deployer

  def setup_suite(self):
    if self._deployer is not None:
      runtime.set_deployer("ztestsuite.unittest.deployer", self._deployer )
    if os.path.isdir("/tmp/ztestsute"):
      shutil.rmtree("/tmp/ztestsuite")
    if not os.path.isdir(runtime.get_active_config("LOGS_DIRECTORY")):
      os.makedirs(runtime.get_active_config("LOGS_DIRECTORY"))
    if not os.path.isdir(runtime.get_active_config("OUTPUT_DIRECTORY")):
      os.makedirs(runtime.get_active_config("OUTPUT_DIRECTORY"))
    sample_code = os.path.join(TEST_DIRECTORY, "samples","trivial_program_with_timing")
    self.ssh.connect("localhost")
    self.sample_code_in, stdout, stderr = self.ssh.exec_command("python {0}".format(sample_code))
    if self._deployer is not None:
      self._deployer.start("ztestsuite.unittest")

  def teardown_suite(self):
    if self.sample_code_in is not None:
      self.sample_code_in.write("quit\n")
      self.sample_code_in.flush()
    if self.ssh is not None:
      with self.ssh.open_sftp() as ftp:
        input_csv = os.path.join(runtime.get_active_config("LOGS_DIRECTORY"), "output.csv")
        input_log = os.path.join(runtime.get_active_config("LOGS_DIRECTORY"), "output.log")
        ftp.get("/tmp/trivial_timed_output.csv", input_csv)
        ftp.get("/tmp/trivial_timed_output", input_log)
        ftp.remove("/tmp/trivial_timed_output.csv")
        ftp.remove("/tmp/trivial_timed_output")
      self.ssh.close()
    if self._deployer is not None:
      self._deployer.stop("ztestsuite.unittest")

  def naarad_config(self):
    return os.path.join(TEST_DIRECTORY, "samples/naarad_config.cfg")


  def process_logs(self, servicename):
    pass
