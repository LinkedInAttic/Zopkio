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

class Config(object):
  """
  Structure used to stores information about a configuration during runtime
  """
  def __init__(self, name, mapping):
    """
    :param name: The name of the configuration
    :param mapping: The actual mapping of the properties of the configuration
    """
    self.name = name
    self.mapping = mapping
    self.result = None
    self.start_time = None
    self.end_time = None
    self.naarad_id = None
    self.message = ""
