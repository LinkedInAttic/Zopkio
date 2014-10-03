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

CONFIG_ABORT = 'Configuration skipped. Too many prior configurations failed setup_suite/teardown_suite consecutively.\n ' \
               'Change the "max_suite_failures_before_abort" field in your master configuration to allow for more failures.\n'

TEST_ABORT = 'Test skipped. Too many prior tests failed setup/teardown consecutively.\n ' \
             'Change the "max_failures_per_suite_before_abort" field in your configuration to allow for more failures.\n'

SETUP_SUITE_FAILED = 'setup_suite() failed. See below for the trace.\n'
TEARDOWN_SUITE_FAILED = 'teardown_suite() failed. See below for the trace.\n'

SETUP_FAILED = 'setup() failed. See below for the trace.\n'
TEARDOWN_FAILED = 'teardown() failed. See below for the trace.\n'
