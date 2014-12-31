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

class Test(object):
  """
  Structure used to store information about a test during runtime
  """
  def __init__(self, name, function, phase):
    """
    :param name: name of the test
    :param function: callback that will be run during test execution
    """
    self.name = name

    self.phase = phase

    self.function = function
    self.validation_function = None

    self.description = None

    self.func_start_time = None
    self.func_end_time = None
    self.start_time = None
    self.end_time = None

    self.result = None
    self.exception = None

    self.naarad_config = None
    self.naarad_id = None
    self.naarad_stats = None
    self.sla_objs = None

    self.message = ""

  def reset(self):
    """
    Reset to a 'clean' state, i.e all test data is reset and only the name and functions are kept
    """

    self.func_start_time = None
    self.func_end_time = None
    self.start_time = None
    self.end_time = None

    self.result = None
    self.exception = None

    self.naarad_config = None
    self.naarad_id = None
    self.naarad_stats = None
    self.sla_objs = None

    self.message = ""
