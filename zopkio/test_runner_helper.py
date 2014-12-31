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
Delegate for non-execution tasks for TestRunner
"""

import json
import logging
import os
import sys
import time

from zopkio.configobj import Config
import zopkio.constants as constants
import zopkio.runtime as runtime
from zopkio.testobj import Test
import zopkio.utils as utils

logger = logging.getLogger(__name__)

def _determine_tests(test_modules):
  """
  Determine a list of tests to run from the provided test modules
  """
  for module in test_modules:
    attrs = dir(module)
    if hasattr(module, "test_phase"):
      test_phase = module.test_phase
    else:
      test_phase = constants.DEFAULT_TEST_PHASE
    # The following is a way to extract the names of all functions in a module
    # An alternative is to use inspect.isfunction but this has better support for 'duck typing'
    functions = set([fun for fun in attrs if hasattr(getattr(module, fun), '__call__')])
    tests = dict([(fun.lower(), Test(fun, getattr(module, fun), test_phase)) for fun in functions if "test" in fun.lower()])
    for fun in functions:
      if "validate" in fun.lower():
        test_name = fun.lower().replace("validate", "test")
        if test_name in tests:
          tests[test_name].validation_function = getattr(module, fun)
    for test in tests.values():
      if test.function.__doc__ is not None:
        test.description = test.function.__doc__
      if test.validation_function is not None:
        if test.validation_function.__doc__ is not None:
          if test.description is not None:
            test.description = "{0};\n{1}".format(test.description, test.validation_function.__doc__)
          else:
            test.description = test.validation_function.__doc__
      yield test


def directory_setup(testfile, perf_module, configs):
  """
  Sets up the output directories.

  :param testfile: the main testfile used in run_test(); only used here for its file name
  :returns: dict with keys ["report_name", "report_dir", "logs_dir"]
  """
  dir_info = {}

  utils.makedirs(runtime.get_reports_dir())

  report_name = os.path.splitext(os.path.basename(testfile))[0]  # getting the file name without extension
  date_time = time.strftime("_%Y%m%d_%H%M%S", time.localtime(runtime.get_init_time()))
  report_name += date_time
  dir_info["report_name"] = report_name

  results_dir = os.path.join(runtime.get_reports_dir(), report_name)
  utils.makedirs(results_dir)
  dir_info["results_dir"] = results_dir

  if "LOGS_DIRECTORY" in configs.mapping:
    logs_dir = configs.mapping.get("LOGS_DIRECTORY")
  else:
    logs_dir = perf_module.LOGS_DIRECTORY
  utils.makedirs(logs_dir)
  dir_info["logs_dir"] = logs_dir

  return dir_info


def get_modules(testfile, tests_to_run, config_overrides):
  """
  Gets modules and objects required to run tests

  :param testfile:
  :param tests_to_run:
  :param config_overrides:
  :return:
  """
  test_dic = _parse_input(testfile)
  master_config, configs = _load_configs_from_directory(test_dic["configs_directory"], config_overrides)
  _setup_paths(master_config.mapping.get("additional_paths", []))
  deployment_module = utils.load_module(test_dic["deployment_code"])
  if  "dynamic_configuration_code" in test_dic:
    perf_module = utils.load_module(test_dic["dynamic_configuration_code"])
  else:
    perf_module = utils.load_module(test_dic["perf_code"])
  test_modules = [utils.load_module(testcode) for testcode in test_dic["test_code"]]
  if tests_to_run is not None:
    tests = [test for test in _determine_tests(test_modules) if test.name in tests_to_run]
  else:
    tests = [test for test in _determine_tests(test_modules)]
  tests_with_phases = {}
  for test in tests:
    tests_with_phases[test.phase] = tests_with_phases.get(test.phase, [])+[test]
  serial_tests = tests_with_phases.pop(constants.DEFAULT_TEST_PHASE, [])
  tests = serial_tests+[test_with_phase[1] for test_with_phase in sorted(tests_with_phases.items(), key=lambda pair: pair[0])]


  return deployment_module, perf_module, tests, master_config, configs


def _load_configs_from_directory(config_dir, overrides):
  """
  Returns a master configuration object and a list of configuration objects

  :param config_dir: the directory where the configuration files are located
  :param overrides: mapping of the command line overrides
  """
  MASTER_CONFIG_FILE_NAME = "master"
  DEFAULT_CONFIG_NAME = "single execution"
  EMPTY_MAP = {}

  master_config = None
  config_objs = []

  # get master config and default mapping
  config_subdirs = []
  default_mapping = {}
  for dir_item in os.listdir(config_dir):
    full_path = os.path.join(config_dir, dir_item)
    if os.path.isdir(full_path):
      config_subdirs.append(full_path)  # save subdirs for processing later
    elif os.path.isfile(full_path):
      config_name = os.path.splitext(os.path.basename(full_path))[0]
      try:
        mapping = utils.parse_config_file(full_path)
      except ValueError:
        logger.debug("Ignored " + full_path + "as configuration due to file extension")
      else:
        if MASTER_CONFIG_FILE_NAME in config_name:
          master_config = Config(MASTER_CONFIG_FILE_NAME, mapping)
        else:
          default_mapping.update(mapping)
  if master_config is None:
    master_config = Config(MASTER_CONFIG_FILE_NAME, EMPTY_MAP)

  if len(config_subdirs) == 0:
    default_mapping.update(overrides)
    config_objs.append(Config(DEFAULT_CONFIG_NAME, default_mapping))
  else:
    # make a config object for each subdir
    for config_subdir in config_subdirs:
      config_files = [os.path.join(config_subdir, config_file) for config_file in os.listdir(config_subdir)
                      if os.path.isfile(os.path.join(config_subdir, config_file))]
      subdir_mapping = default_mapping.copy()  # initialize the configuration as default
      config_name = os.path.basename(config_subdir)
      for config_file in config_files:
        try:
          mapping = utils.parse_config_file(config_file)
        except ValueError:
          logger.debug("Ignored " + config_file + "as configuration due to file extension")
        else:
          subdir_mapping.update(mapping)
      subdir_mapping.update(overrides)
      config_objs.append(Config(config_name, subdir_mapping))

  return master_config, config_objs


def _parse_input(testfile):
  """
  Extract the dictionary from the input file
  """
  ext = os.path.splitext(testfile)[-1].lower()
  if ext == ".py":
    test_dic = utils.load_module(testfile).test
  elif ext == ".json":
    json_data = open(testfile).read()
    test_dic = json.loads(json_data)
  else:
    logger.critical(testfile + " is not supported; currently only supports python and json files")
    raise ValueError("currently only supports python and json files")

  # checking test_dic to see if it has valid keys and values
  if not len(test_dic.keys()) == 4:
    logger.critical("input requires four fields: deployment_code, test_code, perf_code, configs_directory")
    raise ValueError("input requires four fields: deployment_code, test_code, perf_code, configs_directory")

  old_valid_key_list = ["deployment_code", "test_code", "perf_code", "configs_directory"]
  new_valid_key_list = ["deployment_code", "test_code", "dynamic_configuration_code", "configs_directory"]
  if not set(old_valid_key_list) == set(test_dic.keys()) and not set(new_valid_key_list) == set(test_dic.keys()):
    logger.critical("input requires four fields: deployment_code, test_code, dynamic_configuration_code, configs_directory")
    raise ValueError("input requires four fields: deployment_code, test_code, dynamic_configuration_code, configs_directory")

  filename = test_dic["deployment_code"]
  utils.check_file_with_exception(filename)
  filenames = test_dic["test_code"]
  for filename in filenames:
    utils.check_file_with_exception(filename)
  if "dynamic_configuration_code" in test_dic:
    filename = test_dic["dynamic_configuration_code"]
  else:
    filename = test_dic["perf_code"]
  utils.check_file_with_exception(filename)
  dirname = test_dic["configs_directory"]
  utils.check_dir_with_exception(dirname)

  return test_dic


def _setup_paths(paths):
  for path in paths:
    sys.path.append(path)
