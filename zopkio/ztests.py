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

import test_runner
from testobj import Test
import constants

class ZTest(object):
  """
  This class represents a basic zopkio test. It has four functions `setup`, `teardown`, `test`, and `validate` that should be
  overwritten. There are two public attributes `phase` and `iteration`

  Attributes:
    phase: the test phase that this test should be executed in. This defaults to the DEFAULT_TEST_PHASE which means it will
           be executed sequentially before any other test phase
    iteration: the number of times to run this test. This defaults to 1.

  """

  phase = constants.DEFAULT_TEST_PHASE
  iteration = constants.DEFAULT_ITERATION

  def setup(self):
    """
    This runs before the test and can be used for test specific setup
    """
    pass

  def teardown(self):
    """
    This runs after the test and can be used for test specific teardown
    """
    pass

  def test(self):
    """
    This is the main test function.
    """
    pass

  def validate(self):
    """
    This function can be used to do post teardown validation for tests where determining correctness is too expensive
    or challenging to do during the online portion. This runs after the test suite teardown and all logs have been copied
    to the local host.
    """
    pass

class ZTestSuite(object):
  """ This the minimal implementation for a zopkio test. This class can be extended as a convenient way to build
  new tests by simply overriding the public functions. This test has four public functions that should be overwritten
  and one attribute that should be set. The four functions are `setup_suite`, `teardown_suite`, `process_logs`, and
  `naarad_configs`. The attribute is `config_dir`. There are two other functions that only need to be changed if the
  default behavior is not appropriate. These two functions are `get_tests` which will find any ZTest attributes of the
  ZTestSuite instance and create the appropriate Test objects for them and `zopkio` which will run the test using the
  TestRunner.

  Attributes:
    config_dir: The location of the config directory
  """

  config_dir="config"

  def setup_suite(self):
    """
    This runs before any test in the suite for generic setup
    """
    pass

  def teardown_suite(self):
    """
    This runs after all of the tests in the suite for generic teardown
    """
    pass

  def process_logs(self, servicename):
    """
    Lists the logs to copy for each service
    :param servicename: the service to fetch logs for
    :return: the names of the log files to copy
    """
    return []

  def machine_logs(self, process_unique_id):
    """
    Lists the machine logs for the given process
    :param process_unique_id: the unique id for the process running on the machine
    :return: empty list by default
    """
    return []

  def naarad_logs(self, process_unique_id):
    """
    Lists the naarad logs to copy for a given process
    :param process_unique_id: the unique id for the process running on the machine
    :return: empty list by default
    """
    return []

  def log_patterns(self, process_unique_id):
    """
    Return a filter pattern used when fetching logs for a process, applied to the log file name
    :param process_unique_id: the unique id for the process
    :return: filter that matches any file name
    """
    return constants.FILTER_NAME_ALLOW_NONE


  def should_fetch_logs(self):
    #default to always fetch logs for all processes
    return True

  def naarad_config(self):
    """
    This returns the path of the naarad config for use in performance verification
    :return: The path to the naarad config (future versions may support returning a naarad config object if
    the naarad api changes)
    """
    pass

  def get_tests(self, **kwargs):
    """
    This finds all of the ZTest attributes and creates a Test object for each one
    :return: a list of Test objects
    """
    attrs = dir(self)
    testlist = kwargs.get("testlist", None)
    if testlist is not None:
      ztests = [(attr, getattr(self, attr)) for attr in attrs if isinstance(getattr(self, attr), ZTest) and attr in testlist]
    else:
      ztests = [(attr, getattr(self, attr)) for attr in attrs if isinstance(getattr(self, attr), ZTest)]
    tests = [Test(name, ztest.test, phase=ztest.phase, iteration=ztest.iteration, validate=ztest.validate)
             for (name, ztest) in ztests]
    return tests


  def zopkio(self):
    """
    This invokes a test_runner.TestRunner for this ZtestSuite
    """
    runner = test_runner.TestRunner(ztestsuite=self)
    runner.run()
