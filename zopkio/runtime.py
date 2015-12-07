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

from collections import defaultdict
import os
import time

from zopkio.results_collector import ResultsCollector

_init_time = time.time()
_username = None
_password = None
_active_config = None
_active_tests = {}
_machine_names = defaultdict()
_deployers = {}
_collector = ResultsCollector()
_output_dir = os.path.join(os.getcwd(), time.strftime("zopkio_%Y%m%d_%H%M%S", time.localtime(_init_time)))

def get_init_time():
  global _init_time
  return _init_time

def set_init_time(time):
  global _init_time
  _init_time = time

def get_reports_dir():
  return os.path.join(_output_dir, 'reports')

def get_output_dir():
  global _output_dir
  return _output_dir

def set_output_dir(output_dir):
  global _output_dir
  _output_dir = output_dir

def get_username():
  """

  :return: the username of the user running the process (needed for lid)
  """
  global _username
  return _username


def get_password():
  """

  :return: the password of the user (needed for lid)
  """
  global _password
  return _password


def get_machine(machine_name):
  """
  gets the physical machine associated with the name. By default return localhost
  :param machine_name:
  :return:
  """
  global _machine_names
  return _machine_names[machine_name]


def get_deployer(service_name):
  """
  Gets the deployer associated with the service
  :param service_name:
  :return:
  """
  return _deployers[service_name]


def set_user(username, password):
  """
  Private function to set the username and password should only be called from the main function
  :param username:
  :param password:
  :return:
  """
  global _username
  _username = username
  global _password
  _password = password


def set_machines(machines):
  """
  Private function to set the machine mapping should only be called from the main file
  :param machines:
  :return:
  """
  global _machine_names
  _machine_names = machines


def set_deployer(service_name, deployer):
  """
  Specifies the deployer associated with a particular service
  :param service_name:
  :param deployer:
  :return:
  """
  _deployers[service_name] = deployer

def remove_deployer(service_name):
  """
  Remove the deployer with the given name, if it exists
  :param service_name:  name of deployer to remove
  """
  try:
    del _deployers[service_name]
  except:
    pass

def reset_deployers():
  """
  Clear all added deployers
  """
  global _deployers
  _deployers = {}

def get_deployers():
  """
  Returns all known deployers, primarily used internally to handle cleanup and log collection, but available for other use
  :return:
  """
  return _deployers.values()


def get_collector():
  """
  Simulates a singleton collector that can be used globally
  :return: results_collector instantiated with the runtime module
  """
  return _collector

def reset_collector():
  """
  Reset the global collector this is used for testing
  """
  global _collector
  _collector = ResultsCollector()

def reset_all():
  """
  Clear relevant globals to start fresh
  :return:
  """
  global _username
  global _password
  global _active_config
  global _active_tests
  global _machine_names
  global _deployers
  reset_deployers()
  reset_collector()
  _username = None
  _password = None
  _active_config = None
  _active_tests = {}
  _machine_names = defaultdict()

###
# Methods dealing with configurations
###

def set_active_config(config):
  """
  Private function to set the config mapping should only be called from the main file
  :param configs:
  :return:
  """
  global _active_config
  _active_config = config


def get_active_config(config_option, default=None):
  """
  gets the config value associated with the config_option or returns an empty string if the config is not found
  :param config_option:
  :param default: if not None, will be used
  :return: value of config. If key is not in config, then default will be used if default is not set to None. 
  Otherwise, KeyError is thrown.
  """
  return _active_config.mapping[config_option] if default is None else _active_config.mapping.get(config_option, default)

def get_active_config_name():
  return _active_config.name


###
# Methods dealing with tests
###

def set_active_tests(tests):
  global _active_tests
  for test in tests:
    try:
      iteration = iter(test)
      #if test item is itself iterable:
      for individual_test in iteration:
        _active_tests[individual_test.name] = individual_test
    except:
      #if test item is a single test:
      _active_tests[test.name] = test


def get_active_test_start_time(test_name):
  return _active_tests[test_name].start_time


def get_active_test_end_time(test_name):
  return _active_tests[test_name].end_time


def get_active_test_metrics(test_name):
  return _active_tests[test_name].naarad_stats
