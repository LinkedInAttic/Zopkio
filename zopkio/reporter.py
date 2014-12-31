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

    self.report_file_sfx = "_report.html"

    self.home_page = os.path.join(output_dir, "report.html")
    self.log_page = os.path.join(output_dir, "log.html")
    self.project_url = "https://github.com/linkedin/Zopkio"

    self.results_map = {
        "passed": constants.PASSED,
        "failed": constants.FAILED,
        "skipped": constants.SKIPPED
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
    return self.report_info.home_page

  def generate(self):
    """
    Generates the report
    """
    self._setup()

    header_html = self._generate_header()
    footer_html = self._generate_footer()
    results_topbar_html = self._generate_topbar("results")
    summary_topbar_html = self._generate_topbar("summary")
    logs_topbar_html = self._generate_topbar("logs")

    summary_body_html = self._generate_summary_body()
    summary_html = header_html + summary_topbar_html + summary_body_html + footer_html
    Reporter._make_file(summary_html, self.report_info.home_page)

    log_body_html = self._generate_log_body()
    log_html = header_html + logs_topbar_html + log_body_html+footer_html
    Reporter._make_file(log_html, self.report_info.log_page)

    for config_name in self.report_info.config_to_test_names_map.keys():
      config_dir = os.path.join(self.report_info.resource_dir, config_name)
      utils.makedirs(config_dir)

      config_body_html = self._generate_config_body(config_name)
      config_html = header_html + results_topbar_html + config_body_html + footer_html
      config_file = os.path.join(config_dir, config_name + self.report_info.report_file_sfx)
      Reporter._make_file(config_html, config_file)

      for test_name in self.data_source.get_test_names(config_name):
        test_body_html = self._generate_test_body(config_name, test_name)
        test_html = header_html + results_topbar_html + test_body_html + footer_html
        test_file = os.path.join(config_dir, test_name + self.report_info.report_file_sfx)
        Reporter._make_file(test_html, test_file)

  def _generate_config_body(self, config_name):
    summary_stats = [
        self.data_source.count_tests(config_name),
        self.data_source.count_tests_with_result(config_name, constants.PASSED),
        self.data_source.count_tests_with_result(config_name, constants.FAILED),
        self.data_source.count_tests_with_result(config_name, constants.SKIPPED),
        self.data_source.get_config_exec_time(config_name),
        self.data_source.get_config_start_time(config_name),
        self.data_source.get_config_end_time(config_name)
    ]

    config_template = self.env.get_template("config_page.html")
    config_body_html = config_template.render(
        config_data=self.data_source.get_config_result(config_name),
        tests=self.data_source.get_test_results(config_name),
        report_info=self.report_info,
        summary=summary_stats
    )

    return config_body_html


  def _generate_log_body(self):
    log_template = self.env.get_template("logs_page.html")
    log_body_html = log_template.render(logs_dir=self.report_info.logs_dir)
    return log_body_html

  def _generate_footer(self):
    footer_template = self.env.get_template("footer.html")
    footer_html = footer_template.render()
    return footer_html

  def _generate_header(self):
    CSS_INCLUDES = [
        "web_resources/style.css"
    ]
    CSS_INCLUDES[:] = [os.path.join(constants.PROJECT_ROOT_DIR, css_include) for css_include in CSS_INCLUDES]

    JS_INCLUDES = [
        "web_resources/script.js"
    ]
    JS_INCLUDES[:] = [os.path.join(constants.PROJECT_ROOT_DIR, js_include) for js_include in JS_INCLUDES]
    header_template = self.env.get_template("header.html")
    header_html = header_template.render(
        page_title=self.name,
        css_includes=CSS_INCLUDES,
        js_includes=JS_INCLUDES
    )
    return header_html

  def _generate_summary_body(self):
    summary_stats = [
        self.data_source.count_all_tests(),
        self.data_source.count_all_tests_with_result(constants.PASSED),
        self.data_source.count_all_tests_with_result(constants.FAILED),
        self.data_source.count_all_tests_with_result(constants.SKIPPED),
        self.data_source.get_total_config_exec_time(),
        self.data_source.get_summary_start_time(),
        self.data_source.get_summary_end_time()
    ]

    config_failure_map = {}
    config_has_failure_map = {}
    config_has_skipped_map = {}
    for config_name in self.report_info.config_to_test_names_map.keys():
      config_failure_map[config_name] = self.data_source.get_config_result(config_name).result
      config_has_failure_map[config_name] = (self.data_source.count_tests_with_result(config_name, constants.FAILED) > 0)
      config_has_skipped_map[config_name] = (self.data_source.count_tests_with_result(config_name, constants.SKIPPED) > 0)

    summary_template = self.env.get_template("landing_page.html")
    summary_body = summary_template.render(
        report_info=self.report_info,
        summary=summary_stats,
        config_fail=config_failure_map,
        config_has_fail=config_has_failure_map,
        config_has_skip=config_has_skipped_map
    )
    return summary_body

  def _generate_topbar(self, active_page):
    topbar_template = self.env.get_template("topbar.html")
    topbar_html = topbar_template.render(
        report_info=self.report_info,
        active=active_page,
    )
    return topbar_html

  def _generate_test_body(self, config_name, test_name):
    test_template = self.env.get_template("test_page.html")
    test_body = test_template.render(
        config_name=config_name,
        test_data=self.data_source.get_test_result(config_name, test_name),
        report_info=self.report_info
    )
    return test_body

  @staticmethod
  def _make_file(html, location):
    with open(location, "w") as f:
      f.write(html)

  def _setup(self):
    utils.makedirs(self.report_info.output_dir)
    utils.makedirs(self.report_info.resource_dir)
    self.report_info.config_to_test_names_map = self.get_config_to_test_names_map()
