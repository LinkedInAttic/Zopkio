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
import unittest

import zopkio.testobj as testobj
import datetime
import time
import zopkio.runtime as runtime

class TestTestUtils(unittest.TestCase):
  FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))

  def test_get_log_for_test(self):
    """
    Tests if we get the logs for test correctly
    """

    test = testobj.Test("Testing_Logs",None,0,0)
    test.start_time = time.time()
    time.sleep(2)
    test.end_time = time.time()
    runtime.set_active_tests([test])

    output_path = '/tmp/test_test_utils_logs_output'
    if not os.path.exists(output_path):
      os.mkdir(output_path)
    with open(os.path.join(output_path, 'test.log'), 'w') as f:
      f.write('23:59:59 [main] INFO  Testing_Logs')      
    with open(os.path.join(output_path, 'test.log'), 'w') as f:
      f.write('23:59:59 [main] INFO  TestClientService - Sent 100')  

if __name__ == '__main__':
  unittest.main()
