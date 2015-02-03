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
import zopkio.remote_host_helper as remote_host_helper
import shutil
from time import sleep
__test__ = False  # don't this as a test

TEST_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIRECTORY = "/tmp/test_with_naarad/collected_logs/"
OUTPUT_DIRECTORY = "/tmp/test_with_naarad/results/"
__ssh__ = None
__sample_code_in__ = None

test = {
  "deployment_code": os.path.abspath(__file__),
  "test_code": [os.path.abspath(__file__)],
  "dynamic_configuration_code": os.path.abspath(__file__),
  "configs_directory": os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_configs")
}


def setup_suite():
  if os.path.isdir("/tmp/test_with_naarad"):
    shutil.rmtree("/tmp/test_with_naarad")
  if not os.path.isdir(LOGS_DIRECTORY):
    os.makedirs(LOGS_DIRECTORY)
  if not os.path.isdir(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)
  global __ssh__
  __ssh__ = remote_host_helper.sshclient()
  __ssh__.load_system_host_keys()
  __ssh__.connect("localhost")
  sample_code = os.path.join(TEST_DIRECTORY, "samples/trivial_program_with_timing")
  global __sample_code_in__
  __sample_code_in__, stdout, stderr = __ssh__.exec_command("python {0}".format(sample_code))


def teardown_suite():
  if __sample_code_in__ is not None:
    __sample_code_in__.write("quit\n")
    __sample_code_in__.flush()
  if __ssh__ is not None:
    ftp = __ssh__.open_sftp()
    input_csv = os.path.join(LOGS_DIRECTORY, "output.csv")
    input_log = os.path.join(LOGS_DIRECTORY, "output.log")
    ftp.get("/tmp/trivial_timed_output.csv", input_csv)
    ftp.get("/tmp/trivial_timed_output", input_log)
    ftp.remove("/tmp/trivial_timed_output.csv")
    ftp.remove("/tmp/trivial_timed_output")
    ftp.close()
    __ssh__.close()


def test0():
  """
  Yay! Docstring!
  """
  assert 1 == 2


def test1():
  __sample_code_in__.write("test1\n")
  __sample_code_in__.flush()
  sleep(5)
  with open("/tmp/trivial_timed_output", "r") as f:
    lines = f.readlines()
    test_str = "".join(lines)
    assert "test1" in test_str


def test2():
  """
  Another docstring
  """
  for i in xrange(50, 150):
    __sample_code_in__.write("{0}\n".format(i))
    __sample_code_in__.flush()
    sleep(.05)


def test3():
    assert 1 == 1


def validate2():
  assert 1 == 1


def naarad_config(config, test_name=None):
  return os.path.join(TEST_DIRECTORY, "samples/naarad_config.cfg")


class MockConfig(object):
  """
  Mock config class currently only has a name so that I can use it in execute run and an empty config map
  """
  def __init__(self, name):
    self.name = name
    self.mapping = {}
