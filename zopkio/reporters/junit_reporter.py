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

"""
Class used to generate the report.
"""
import os
from jinja2 import Environment, FileSystemLoader

import zopkio.constants as constants
import zopkio.runtime as runtime
import zopkio.utils as utils
from junit_xml import TestSuite, TestCase


class _ReportInfo(object):
  """
  Holds data shared among all report pages
  """
  def __init__(self, output_dir, logs_dir, naarad_dir):
    self.output_dir = os.path.abspath(output_dir)
    self.resource_dir = os.path.join(output_dir, "resources/")
    self.logs_dir = os.path.abspath(logs_dir)
    self.naarad_dir = os.path.abspath(naarad_dir)

    self.config_to_test_names_map = {}
    self.junit_xml_path = output_dir

    self.results_map = {
        "passed": constants.PASSED,
        "failed": constants.FAILED,
        "skipped": constants.SKIPPED,
        # "error": constants.ERROR
    }


class Reporter(object):
  """
  Class that converts the aggregated output into a user-friendly web page.
  """
  def __init__(self, report_name, output_dir, logs_dir, naarad_dir):
    """
    :param report_name: used in the title of the front-end
    :param output_dir: directory where the report will be generated
    :param logs_dir: directory of where the logs will be collected
    :param naarad_dir: directory containing the naarad reports
    """
    self.name = report_name
    self.env = Environment(loader=FileSystemLoader(constants.WEB_RESOURCE_DIR))  # used to load html pages for Jinja2
    self.data_source = runtime.get_collector()
    self.report_info = _ReportInfo(output_dir, logs_dir, naarad_dir)

  def get_config_to_test_names_map(self):
    config_to_test_names_map = {}
    for config_name in self.data_source.get_config_names():
      config_to_test_names_map[config_name] = self.data_source.get_test_names(config_name)
    return config_to_test_names_map

  def get_report_location(self):
    """
    Returns the filename of the landing page
    """
    return os.path.join(self.report_info.junit_xml_path, '_junit_reports.xml')

  def generate(self):
    """
    Generates the report
    """
    self._setup()

    testsuites = []
    for config_name in self.report_info.config_to_test_names_map.keys():
      config_dir = os.path.join(self.report_info.resource_dir, config_name)
      utils.makedirs(config_dir)
      testsuite = self._generate_junit_xml(config_name)
      # print "JUNIT TEST FORMAT------------------------------"
      # print(TestSuite.to_xml_string([testsuites]))
      with open(os.path.join(self.report_info.junit_xml_path, '_junit_reports.xml'), 'w') as file:
          TestSuite.to_file(file, [testsuite], prettyprint=False)

  def _generate_junit_xml(self, config_name):
      testcases = []
      summary_stats = [
        self.data_source.count_tests(config_name),
        self.data_source.count_tests_with_result(config_name, constants.PASSED),
        self.data_source.count_tests_with_result(config_name, constants.FAILED),
        self.data_source.count_tests_with_result(config_name, constants.SKIPPED),
        self.data_source.get_config_exec_time(config_name),
        self.data_source.get_config_start_time(config_name),
        self.data_source.get_config_end_time(config_name)
      ]
      config_data=self.data_source.get_config_result(config_name)
      tests=self.data_source.get_test_results(config_name)
      for test in tests:
          test_time = 0
          if test.func_end_time != None and test.func_start_time != None:
              test_time = test.func_end_time - test.func_start_time
          tc = TestCase(test.name,'',test_time, test.result, test.message)
          if 'failed' in test.result:
              tc.add_failure_info(test.message)
          elif 'skipped' in test.result:
              tc.add_skipped_info(test.message)
          testcases.append(tc)
      testsuite = TestSuite(config_name+self.name, testcases)
      # report_info=self.report_info
      # summary=summary_stats
      return testsuite

  def _setup(self):
    utils.makedirs(self.report_info.output_dir)
    utils.makedirs(self.report_info.resource_dir)
    self.report_info.config_to_test_names_map = self.get_config_to_test_names_map()