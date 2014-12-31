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

import copy
import datetime
import time

import zopkio.constants as constants

class Results(object):
  def __init__(self, config, tests):
    """
    :param config: config object
    :param tests: {test.name: test object}
    """
    self.config_result = config
    self.test_results = tests


class ResultsCollector(object):
  """
  Provides a way to store intermediate results with fast access to individual results.
  Also provides common aggregation functions for the results.
  """
  def __init__(self):
    self.results = {}
    self.start_time = time.time()
    self.end_time = None

  def collect(self, config, tests):
    test_results = {}
    if config.result != constants.SKIPPED:
      for test in tests:
        test_results[test.name] = copy.copy(test)
    self.results[config.name] = Results(copy.copy(config), test_results)

  def count_tests(self, config_name):
    """

    :param config_name:
    :return: total number of tests ran under config_name
    """
    return len(self.results[config_name].test_results)

  def count_tests_with_result(self, config_name, result_type):
    """
    Count the number of tests of a configuration with a certain result
    :param config_name: name of the configuration
    :param result_type: constants.PASSED, constants.FAILED, constants.SKIPPED
    :return: the number of tests in config_name where test.result == result_type
    """
    return sum(test_data.result == result_type for test_data in self.results[config_name].test_results.values())

  def get_test_exec_time(self, config_name, test_name):
    test_data = self.results[config_name].test_results[test_name]
    if test_data.start_time is None or test_data.end_time is None:
      return None
    return test_data.end_time - test_data.start_time

  def get_test_start_time(self, config_name, test_name):
    test_data = self.results[config_name].test_results[test_name]
    if test_data.start_time is None:
      return None
    return datetime.datetime.fromtimestamp(test_data.start_time).strftime('%Y-%m-%d %H:%M:%S')

  def get_test_end_time(self, config_name, test_name):
    test_data = self.results[config_name].test_results[test_name]
    if test_data.end_time is None:
      return None
    return datetime.datetime.fromtimestamp(test_data.end_time).strftime('%Y-%m-%d %H:%M:%S')

  def count_all_tests(self):
    """

    :return: total number of tests ran under all configs
    """
    return sum(self.count_tests(config_name) for config_name in self.results.keys())

  def count_all_tests_with_result(self, result_type):
    """
    Count total number of tests with a certain result
    :param result_type: constants.PASSED, constants.FAILED, constants.SKIPPED
    :return: the number of tests where test.result == result_type
    """
    return sum(self.count_tests_with_result(config_name, result_type) for config_name in self.results.keys())

  def get_config_exec_time(self, config_name):
    config_data = self.results[config_name].config_result
    if config_data.start_time is None or config_data.end_time is None:
      return None
    return config_data.end_time - config_data.start_time

  def get_config_start_time(self, config_name):
    config_data = self.results[config_name].config_result
    if config_data.start_time is None:
      return None
    return datetime.datetime.fromtimestamp(config_data.start_time).strftime('%Y-%m-%d %H:%M:%S')

  def get_config_end_time(self, config_name):
    config_data = self.results[config_name].config_result
    if config_data.end_time is None:
      return None
    return datetime.datetime.fromtimestamp(config_data.end_time).strftime('%Y-%m-%d %H:%M:%S')

  def get_total_config_exec_time(self):
    """

    :return: total execution time of all configurations
    """
    sum_exec_time = 0
    for config_name in self.results.keys():
      exec_time = self.get_config_exec_time(config_name)
      if exec_time is not None:
        sum_exec_time += exec_time

    return sum_exec_time

  def get_summary_start_time(self):
    """

    :return: start time of test
    """

    return datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')

  def get_summary_end_time(self):
    """

    :return: end time of test
    """
    if self.end_time is None:
      return None
    return datetime.datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S')


  def get_config_result(self, config_name):
    return self.results[config_name].config_result

  def get_test_result(self, config_name, test_name):
    return self.results[config_name].test_results[test_name]

  def get_test_results(self, config_name):
    return self.results[config_name].test_results.values()

  def get_config_names(self):
    return self.results.keys()

  def get_test_names(self, config_name):
    return self.results[config_name].test_results.keys()
