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
import logging
import os
import time
import traceback
import sys

import zopkio.constants as constants
import zopkio.runtime as runtime
from zopkio.test_runner import TestRunner
import zopkio.utils as utils

def setup_logging(output_dir):
  date_time = time.strftime("_%Y%m%d_%H%M%S",
                            time.localtime(runtime.get_init_time()))
  log_dir = os.path.join(output_dir, "logs", "zopkio_log" + date_time)
  utils.makedirs(log_dir)
  log_file = os.path.join(log_dir, "zopkio_log" + date_time + ".log")
  logging.basicConfig(filename=log_file,
                      filemode='a',
                      format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
                      datefmt="%Y-%m-%d %H:%M:%S",
                      level=logging.INFO)

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
  args = parser.parse_args()

  # Get output directory.
  try:
    if args.output_dir is not None:
      runtime.set_output_dir(args.output_dir)
  except ValueError as e:
    print str(e)
    sys.exit(1)

  # Set up logging.
  runtime.set_init_time(time.time())
  setup_logging(runtime.get_output_dir())
  logger = logging.getLogger("zopkio")
  logger.info("Starting zopkio")

  try:
    utils.check_file_with_exception(args.testfile)
    machines = utils.make_machine_mapping(args.machine_list)
    config_overrides = utils.parse_config_list(args.config_overrides)
  except ValueError as e:
    print("Error in processing command line arguments:\n %s" %
          traceback.format_exc())
    sys.exit(1)

  runtime.set_machines(machines)
  user = getpass.getuser()
  password = getpass.getpass()
  runtime.set_user(user, password)

  try:
    test_runner = TestRunner(args.testfile, args.test_list, config_overrides)
  except BaseException as e:
    print("Error setting up testrunner:\n%s" % traceback.format_exc())
    sys.exit(1)

  test_runner.run()

  logger.info("Exiting zopkio")

if __name__ == "__main__":
  main()
