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
Utilities class provides general-use functions for all modules
"""

import logging
import json
import os
import sys

import zopkio.constants as constants

logger = logging.getLogger(__name__)

def check_dir_with_exception(dirname):
  """
  Checks if the directory exists; if not, throw an exception
  """
  if not os.path.isdir(dirname):
    raise ValueError(dirname + " is not a directory")


def check_file_with_exception(filename):
  """
  Checks if the file exists; if not, throw an exception
  """
  if not os.path.isfile(filename):
    raise ValueError(filename + " is not a file")

def check_testfile_dir_structure(filename):
  """
  Checks if the test file has correct directory structure for importing as module
  Makes sure there is no directory with same testfile name to cause conflict
  """
  dirname =  os.path.splitext(filename)[0]
  if os.path.isdir(dirname):
    raise ValueError('incorrect dir structure testfile:%s exist in same level as dir:%s' %(filename,dirname))


def load_module(filename):
  """
  Loads a module by filename
  """
  basename = os.path.basename(filename)
  path = os.path.dirname(filename)
  sys.path.append(path)
  # TODO(tlan) need to figure out how to handle errors thrown here
  return __import__(os.path.splitext(basename)[0])


def makedirs(path):
  """
  Makes directories without raising an error if the directory already exists
  :param path: the path of the directory
  :return:
  """
  if not os.path.exists(path):
    os.makedirs(path)


def make_machine_mapping(machine_list):
  """
  Convert the machine list argument from a list of names into a mapping of logical names to
  physical hosts. This is similar to the _parse_configs function but separated to provide the
  opportunity for extension and additional checking of machine access
  """
  if machine_list is None:
    return {}
  else:
    mapping = {}
    for pair in machine_list:
      if (constants.MACHINE_SEPARATOR not in pair) or (pair.count(constants.MACHINE_SEPARATOR) != 1):
        raise ValueError("machine pairs must be passed as two strings separted by a %s", constants.MACHINE_SEPARATOR)
      (logical, physical) = pair.split(constants.MACHINE_SEPARATOR)
      # add checks for reachability
      mapping[logical] = physical
    return mapping


def parse_config_list(config_list):
  """
  Parse a list of configuration properties separated by '='
  """
  if config_list is None:
    return {}
  else:
    mapping = {}
    for pair in config_list:
      if (constants.CONFIG_SEPARATOR not in pair) or (pair.count(constants.CONFIG_SEPARATOR) != 1):
        raise ValueError("configs must be passed as two strings separted by a %s", constants.CONFIG_SEPARATOR)
      (config, value) = pair.split(constants.CONFIG_SEPARATOR)
      mapping[config] = value
    return mapping


def parse_config_file(config_file_path):
  """
  Parse a configuration file. Currently only supports .json, .py and properties separated by '='
  :param config_file_path:
  :return: a dict of the configuration properties
  """
  extension = os.path.splitext(config_file_path)[1]
  if extension == '.pyc':
    raise ValueError("Skipping .pyc file as config")
  if extension == '.json':
    with open(config_file_path) as config_file:
      try:
        mapping = json.load(config_file)
      except ValueError as e:
        logger.error("Did not load json configs", e)
        raise SyntaxError('Unable to parse config file:%s due to malformed JSON. Aborting' %(config_file_path))
  elif extension == '.py':
    mapping = {}
    file_dict = load_module(config_file_path)
    for attr_name in dir(file_dict):
      if not (attr_name.startswith('_') or attr_name.startswith('__')):
        attr = getattr(file_dict, attr_name)
        if type(attr) is dict:
          mapping.update(attr)
  else:
    with open(config_file_path) as config_file:
      lines = [line.rstrip() for line in config_file if line.rstrip() != "" and not line.startswith("#")]
      mapping = parse_config_list(lines)

  return mapping
