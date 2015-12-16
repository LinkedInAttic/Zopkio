#!/usr/bin/env python
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
This is the core engine for executing a distributed functional and performance
test. Minimal logic will be done in this class.
"""

import argparse
import getpass
import inspect
import logging
import os
import traceback
import sys

import zopkio.constants as constants
import zopkio.runtime as runtime
from zopkio.test_runner import TestRunner
from zopkio.ztests import ZTestSuite
import zopkio.utils as utils

def setup_logging(output_dir, log_level, console_level):
  log_dir = os.path.join(output_dir, "logs", "zopkio_log")
  utils.makedirs(log_dir)
  log_file = os.path.join(log_dir, "zopkio_log.log")
  logging.basicConfig(filename=log_file,
                      filemode='a',
                      format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
                      datefmt="%Y-%m-%d %H:%M:%S",
                      level=string_to_level(log_level))
  console = logging.StreamHandler()
  console.setLevel(string_to_level(console_level))
  console.setFormatter(logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s"))
  logging.getLogger('').addHandler(console)

def string_to_level(log_level):
  """
  Converts a string to the corresponding log level
  """
  if (log_level.strip().upper() == "DEBUG"):
    return logging.DEBUG
  if (log_level.strip().upper() == "INFO"):
    return logging.INFO
  if (log_level.strip().upper() == "WARNING"):
    return logging.WARNING
  if (log_level.strip().upper() == "ERROR"):
    return logging.ERROR

def main():
  """
  Parse command line arguments and then run the test suite
  """
  parser = argparse.ArgumentParser(description='A distributed test framework')
  parser.add_argument('testfile',
      help='The file that is used to determine the test suite run')
  parser.add_argument('--test-only',
      nargs='*',
      dest='test_list',
      help='run only the named tests to help debug broken tests')
  parser.add_argument('--machine-list',
      nargs='*',
      dest='machine_list',
      help='''mapping of logical host names to physical names allowing the same
              test suite to run on different hardware, each argument is a pair
              of logical name and physical name separated by a =''')
  parser.add_argument('--config-overrides',
      nargs='*',
      dest='config_overrides',
      help='''config overrides at execution time, each argument is a config with
              its value separated by a =. This has the highest priority of all
              configs''')
  parser.add_argument('-d', '--output-dir',
      dest='output_dir',
      help='''Directory to write output files and logs. Defaults to the current
              directory.''')
  parser.add_argument("--log-level", dest="log_level", help="Log level (default INFO)", default="INFO")
  parser.add_argument("--console-log-level", dest="console_level", help="Console Log level (default ERROR)",
                      default="ERROR")
  parser.add_argument("--nopassword", action='store_true', dest="nopassword", help="Disable password prompt")
  parser.add_argument("--user", dest="user", help="user to run the test as (defaults to current user)")
  args = parser.parse_args()
  try:
    call_main(args)
  except ValueError:
    #We only sys.exit here, as call_main is used as part of a unit test
    #and should not exit the system
    sys.exit(1)

def call_main(args):
  # Get output directory.
  try:
    if args.output_dir is not None:
      runtime.set_output_dir(args.output_dir)
  except ValueError as e:
    print str(e)
    raise

  # Set up logging.
  setup_logging(runtime.get_output_dir(), args.log_level, args.console_level)
  logger = logging.getLogger("zopkio")
  logger.info("Starting zopkio")

  try:
    utils.check_file_with_exception(args.testfile)
    utils.check_testfile_dir_structure(args.testfile)
    machines = utils.make_machine_mapping(args.machine_list)
    config_overrides = utils.parse_config_list(args.config_overrides)
  except ValueError as e:
    logger.error(str(e))
    print("Error in processing command line arguments:\n {0}".format(traceback.format_exc()))
    raise

  runtime.set_machines(machines)
  if args.user is not None:
    user = args.user
  else:
    user = getpass.getuser()
  if args.nopassword:
    password = ""
  else:
    password = getpass.getpass()
  runtime.set_user(user, password)

  try:
    testmodule = utils.load_module(args.testfile)
    ztestsuites = [getattr(testmodule, attr)
               for attr in dir(testmodule)
               if isinstance(getattr(testmodule, attr), ZTestSuite)]
    if len(ztestsuites) > 0: #TODO(jehrlich) intelligently handle multiple test suites
      test_runner = TestRunner(ztestsuite=ztestsuites[0], testlist=args.test_list, config_overrides=config_overrides)
    else:
      test_runner = TestRunner(args.testfile, args.test_list, config_overrides)
  except BaseException as e:
    print("Error setting up testrunner:\n%s" % traceback.format_exc())
    raise ValueError(e.message)

  test_runner.run()

  logger.info("Exiting zopkio")
  return test_runner.success_count(), test_runner.fail_count()

if __name__ == "__main__":
  main()
