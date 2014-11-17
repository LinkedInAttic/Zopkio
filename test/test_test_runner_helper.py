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

import zopkio.configobj as configobj
import zopkio.test_runner_helper as test_runner_helper
import zopkio.runtime as runtime
import zopkio.utils as utils

class TestTestRunnerHelper(unittest.TestCase):
  FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))

  def test_determine_tests_read_correct_number_of_tests_in_file(self):
    """
    Test that we can read the correct number of tests from the test file
    """
    test_directory = os.path.join(self.FILE_LOCATION, "samples/determine_tests")
    test_files = [file_name for file_name in os.listdir(test_directory)
        if os.path.splitext(file_name)[1] == ".py"]
    for testfile in test_files:
      test_module = utils.load_module(os.path.join(test_directory, testfile))
      tests = [test.name for test
          in test_runner_helper._determine_tests([test_module])]

      if ("empty" in testfile) or ("invalid" in testfile) or ("no_test" in testfile):
        self.assertEqual(len(tests), 0)
      elif ("single" in testfile) or ("no_validate" in testfile) or ("no_match" in testfile):
        self.assertEqual(len(tests), 1)
        for i in xrange(0, 1):
          self.assertTrue("test{0}".format(i) in tests)
      elif "multi" in testfile:
        self.assertEqual(len(tests), 2)
        for i in xrange(0, 2):
          self.assertTrue("test{0}".format(i) in tests)
      else:
        print testfile + " was not used as test input"

  def test_determine_tests_read_correct_total_number_of_tests_in_files(self):
    """
    Tests that determine_tests works for a list of modules
    """
    test_directory = os.path.join(self.FILE_LOCATION, "samples/determine_tests")
    test_files = [file_name for file_name in os.listdir(test_directory)
        if os.path.splitext(file_name)[1] == ".py"]
    test_modules = [utils.load_module(os.path.join(test_directory, test_file))
        for test_file in test_files]
    tests = test_runner_helper._determine_tests(test_modules)

    self.assertEqual(sum(1 for test in tests), 5)

  def test_determine_tests_generates_correct_test_object(self):
    """
    Tests that determine_tests generate correct test objects
    """
    test_directory = os.path.join(self.FILE_LOCATION, "samples/determine_tests")
    test_module = utils.load_module(os.path.join(test_directory,
                                                 "meta_test_single.py"))
    single_test_iterator = test_runner_helper._determine_tests([test_module])
    test = next(single_test_iterator)

    self.assertEqual(test.name, "test0")
    self.assertTrue(test.validation_function is not None)
    self.assertEqual(test.validation_function.__name__, "validate0")

  def test_directory_setup_makes_correct_directories(self):
    """
    Tests that directory_setup makes the correct directories
    """
    perf_module = utils.load_module(os.path.join(self.FILE_LOCATION,
                                                 "samples/sample_perf.py"))
    dir_info = test_runner_helper.directory_setup(
        os.path.join(self.FILE_LOCATION, "samples/sample_input.py"),
        perf_module, configobj.Config("Master", {}))
    self.assertTrue(os.path.isdir(runtime.get_reports_dir()))
    self.assertTrue("sample_input" in dir_info["report_name"])
    self.assertTrue(os.path.isdir(dir_info["results_dir"]))
    self.assertTrue(os.path.isdir(dir_info["logs_dir"]))

    shutil.rmtree(dir_info["results_dir"])
    shutil.rmtree(dir_info["logs_dir"])

  def test_load_configs_from_directory_returns_correct_config_objects(self):
    """
    Tests that load_configs_from_directory returns correct config objects
    """
    master_config, configs = test_runner_helper._load_configs_from_directory(
        os.path.join(self.FILE_LOCATION, "samples/sample_configs"), {})
    self.assertEqual(len(configs), 2)
    config_names = [config.name for config in configs]
    self.assertTrue("sample_config1" in config_names)
    self.assertTrue("sample_config2" in config_names)
    all_config_mappings = dict(configs[0].mapping.items() + configs[1].mapping.items())
    self.assertEqual(all_config_mappings["BAR"], "baz")

  def test_load_configs_from_directory_returns_correct_config_objects_with_overrides(self):
    """
    Tests that load config from directory returns correct config objects with
    overrides.
    """
    master_config, configs = test_runner_helper._load_configs_from_directory(
      os.path.join(self.FILE_LOCATION, "samples/sample_configs"), {"a": "z"})
    self.assertEqual(len(configs), 2)
    config_names = [config.name for config in configs]
    self.assertTrue("sample_config1" in config_names)
    self.assertTrue("sample_config2" in config_names)
    all_config_mappings = dict(configs[0].mapping.items() + configs[1].mapping.items())
    self.assertEqual(all_config_mappings["BAR"], "baz")
    self.assertEqual(all_config_mappings["a"], "z")

  def test_parse_input_returns_correct_test_dic(self):
    """
    Tests the private function to read the input test file and produce a
    dictionary.
    """
    test = {
      "deployment_code": "test/samples/sample_deployment.py",
      "test_code": [
          "test/samples/sample_test1.py",
          "test/samples/sample_test2.py"],
      "perf_code": "test/samples/sample_perf.py",
      "configs_directory": "test/samples/sample_configs"
    }

    # relative path
    py_input = test_runner_helper._parse_input("test/samples/sample_input.py")
    # absolute path
    json_input = test_runner_helper._parse_input(
        os.path.join(self.FILE_LOCATION, "samples/sample_input.json"))
    self.assertEqual(py_input, test)
    self.assertEqual(json_input, test)
    self.assertRaises(ImportError, test_runner_helper._parse_input,
                      os.path.join(self.FILE_LOCATION, "invalid_file.py"))
    self.assertRaises(ValueError, test_runner_helper._parse_input,
                      os.path.join(self.FILE_LOCATION, "test_main.pyc"))

if __name__ == '__main__':
  unittest.main()
