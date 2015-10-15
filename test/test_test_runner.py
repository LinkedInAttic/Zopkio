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

from zopkio.test_runner import TestRunner
import zopkio.runtime as runtime
from samples.sample_ztestsuite import SampleTestSuite
from test.mock import Mock_Deployer
from zopkio.configobj import Config

class TestTestRunner(unittest.TestCase):
  FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))

  def test_full_run(self):
    """
    Tests a full run
    """
    runtime.reset_collector()
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_with_naarad.py")
    test_runner = TestRunner(test_file, ["test0", "test1", "test2"], {})
    test_runner.run()

  def test_full_run_parallel(self):
    """
    Tests a full run with parallel tests
    """
    runtime.reset_collector()
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_with_naarad_run_tests_in_parallel.py")
    test_runner = TestRunner(test_file, ["test0", "test1", "test2"], {})
    test_runner.run()

  def test_full_run_with_skip(self):
    """
    Tests failing setup for one test and having it skip
    """
    runtime.reset_collector()
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
    runtime.reset_collector()
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
    runtime.reset_collector()
    test_file = os.path.join(self.FILE_LOCATION,
                             "samples/sample_test_fail_setup_suite.py")
    test_runner = TestRunner(test_file, None,
                             {"max_suite_failures_before_abort": 0})
    test_runner.run()

  def test_full_run_ztestsuite(self):
    """
    Tests the new use of ztest and zetestsuite
    :return:
    """
    runtime.reset_collector()
    ztestsuite = SampleTestSuite()
    ztestsuite.zopkio()

  def test_copy_logs_empty_default(self):
    #first set things up
    runtime.reset_all()
    ztestsuite = SampleTestSuite()
    runtime.set_active_config(Config("unittestconfig",{}))
    runner = TestRunner(ztestsuite=ztestsuite)
    #create a temp dir for logs
    import tempfile
    logs_dir = tempfile.mkdtemp()
    runner.set_logs_dir(logs_dir)
    runner._copy_logs()
    try:
      #no logs specified on default, so should not have any files
     self.assertTrue( os.listdir(logs_dir) == [])
    except:
      raise
    finally:
      #cleanup
      shutil.rmtree( logs_dir)

  def __test_copy_log_speced_per_id(self, ztestsuite, localhost_log_file, fetch_logs_flag = True):
    """
    base test method containing common code called by public test methods for testing execution
    of copy of logs based on function signatures
    """
    import tempfile
    runtime.reset_collector()
    #create the log file on "remote" which is actually localhost
    with open( localhost_log_file, 'wb') as f:
      f.write("This is a log")
    runner = TestRunner(ztestsuite=ztestsuite, config_overrides={"should_fetch_logs":fetch_logs_flag})
    logs_dir = tempfile.mkdtemp()
    runner.set_logs_dir(logs_dir)
    try:
      runner.run()
      #no logs specified on default, so should not have any files
      if fetch_logs_flag:
        self.assertEqual( os.listdir(logs_dir), ['ztestsuite.unittest-' + os.path.basename(localhost_log_file)])
      else:
        self.assertEqual( os.listdir(logs_dir),[])
    except:
      raise
    finally:
      #cleanup
      shutil.rmtree( logs_dir)

  def __test_copy_logs_deprecated(self, ztestsuite, localhost_log_file, fetch_logs_flag = True):
    """
    base test method containing common code called by public test methods for testing execution
    of copy of logs based on deprecated function signatures
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    runtime.reset_all()
    #create the log file on "remote" which is actually localhost
    with open( localhost_log_file, 'wb') as f:
      f.write("This is a log")
    runner = TestRunner(ztestsuite=ztestsuite, should_fetch_logs=fetch_logs_flag)
    logs_dir = tempfile.mkdtemp()
    runner.set_logs_dir(logs_dir)
    try:
      runner.run()
      #no logs specified on default, so should not have any files
      if fetch_logs_flag:
        self.assertEqual( os.listdir(logs_dir), ['ztestsuite.unittest-' + os.path.basename(localhost_log_file)])
      else:
        self.assertEqual( os.listdir(logs_dir),[])
    except:
      raise
    finally:
      #cleanup
      shutil.rmtree( logs_dir)


  def test_copy_log_machine_logs_speced_per_id(self):
    """
    Create a single log file and set "machine_logs" method to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.machine_logs = lambda unique_id: [localhost_log_file]
      self.__test_copy_log_speced_per_id(ztestsuite, localhost_log_file, False)
    finally:
      shutil.rmtree( localhost_logs_dir)

  def test_copy_log_machine_logs_flag_off(self):
    """
    Create a single log file and set "machine_logs" method to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.machine_logs = lambda unique_id: [localhost_log_file]
      ztestsuite.should_fetch_logs = lambda:False
      self.__test_copy_log_speced_per_id(ztestsuite, localhost_log_file, False)
    finally:
      shutil.rmtree( localhost_logs_dir)

  def test_copy_log_machine_logs_deprecated(self):
    """
    Create a single log file and set "machine_logs" method
    with DEPRECATED signature to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.machine_logs = lambda : {"ztestsuite.unittest":[localhost_log_file]}
      self.__test_copy_logs_deprecated(ztestsuite, localhost_log_file)
    finally:
      shutil.rmtree( localhost_logs_dir)

  def test_copy_log_process_logs_speced_per_id(self):
    """
    Create a single log file and set "process_logs" method to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.process_logs = lambda unique_id: [localhost_log_file]
      self.__test_copy_log_speced_per_id(ztestsuite, localhost_log_file, False)
    finally:
      shutil.rmtree( localhost_logs_dir)

  def test_copy_log_process_logs_deprecated(self):
    """
    Create a single log file and set "process_logs" method
    with DEPRECATED signature to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.process_logs = lambda : {"ztestsuite.unittest-srv":[localhost_log_file]}
      self.__test_copy_logs_deprecated(ztestsuite, localhost_log_file)
    finally:
      shutil.rmtree( localhost_logs_dir)

  def test_copy_log_naarad_logs_speced_per_id(self):
    """
    Create a single log file and set "naarad_logs" method to return
    this file and test that is gets copied as expected
    """    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.naarad_logs = lambda unique_id: [localhost_log_file]
      self.__test_copy_log_speced_per_id(ztestsuite, localhost_log_file, False)
    finally:
      #cleanup
      shutil.rmtree( localhost_logs_dir)


  def test_copy_log_naarad_logs_deprecated(self):
    """
    Create a single log file and set "naarad_logs" method
    with DEPRECATED signature to return
    this file and test that is gets copied as expected
    """
    #first set things up
    #create a temp dir for logs
    import tempfile
    localhost_logs_dir = tempfile.mkdtemp()
    try:
      localhost_log_file = os.path.join(localhost_logs_dir, "unittest.log")
      ztestsuite = SampleTestSuite(Mock_Deployer())
      ztestsuite.naarad_logs = lambda : {"ztestsuite.unittest":[localhost_log_file]}
      self.__test_copy_logs_deprecated(ztestsuite, localhost_log_file)
    finally:
      #cleanup
      shutil.rmtree( localhost_logs_dir)


if __name__ == '__main__':
  unittest.main()
