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
import unittest

from zopkio.test_runner import TestRunner

class TestTestRunner(unittest.TestCase):
  FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))

  def test_full_run(self):
    """
    Tests a full run
    """
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_with_naarad.py")
    test_runner = TestRunner(test_file, ["test0", "test1", "test2"], {})
    test_runner.run()

  def test_full_run(self):
    """
    Tests a full run with parallel tests
    """
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_with_naarad_run_tests_in_parallel.py")
    test_runner = TestRunner(test_file, ["test0", "test1", "test2"], {})
    test_runner.run()

  def test_full_run_with_skip(self):
    """
    Tests failing setup for one test and having it skip
    """
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_fail_first_setup.py")
    test_runner = TestRunner(test_file, None,
                             {"max_failures_per_suite_before_abort": -1})
    test_runner.run()

  def test_full_run_with_skip_and_stop_one_config(self):
    """
    Tests failing consecutive setups and having the entire execution of a
    configuration stop.
    """
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_fail_all_setup.py")
    test_runner = TestRunner(test_file, None,
                             {"max_failures_per_suite_before_abort": 0})
    test_runner.run()

  def test_full_run_with_skip_and_stop_all_config(self):
    """
    Tests failing consectutive setup_suites and skipping the rest of the
    configurations.
    """
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_fail_setup_suite.py")
    test_runner = TestRunner(test_file, None,
                             {"max_suite_failures_before_abort": 0})
    test_runner.run()

if __name__ == '__main__':
  unittest.main()
