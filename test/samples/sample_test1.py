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
from time import sleep
__test__ = False  # don't have nose run this as a test
TEST_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGS_DIRECTORY = "/tmp/test1/collected_logs/"
OUTPUT_DIRECTORY = "/tmp/test1/results/"
__ssh__ = None
__sample_code_in__ = None


def setup_suite():
  global __ssh__
  __ssh__ = remote_host_helper.sshclient()
  __ssh__.load_system_host_keys()
  __ssh__.connect("localhost")
  sample_code = os.path.join(TEST_DIRECTORY, "samples/trivial_program")
  global __sample_code_in__
  __sample_code_in__, stdout, stderr = __ssh__.exec_command("python {0}".format(sample_code))


def teardown_suite():
  __sample_code_in__.write("quit")
  __sample_code_in__.flush()
  stdin, stdout, stderr = __ssh__.exec_command("rm /tmp/trivial_output")


def test0():
  assert 1 == 1


def test1():
  __sample_code_in__.write("test1")
  __sample_code_in__.flush()
  sleep(5)
  with open("/tmp/trivial_output", "r") as f:
    lines = f.readlines()
    assert "test1" in lines


def test2():
  pass


def validate1():
  pass


def naarad_config(config, test_name=None):
 return os.path.join(TEST_DIRECTORY, "samples/naarad_config")


class MockConfig(object):
  """
  Mock config class currently only has a name so that I can use it in execute run and an empty config map
  """

  def __init__(self, name):
    self.name = name
    self.configs = {}
