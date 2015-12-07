# Copyright 2015 LinkedIn Corp.
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

LOGS_DIRECTORY = "/tmp/zopkio_zookeeper/logs/"
OUTPUT_DIRECTORY = "/tmp/zopkio_zookeeper/results/"

def machine_logs():
  return {
    "zookeeper1": [os.path.join("/tmp/zookeeper_test1", "zookeeper.out")],
    "zookeeper2": [os.path.join("/tmp/zookeeper_test2", "zookeeper.out")],
    "zookeeper3": [os.path.join("/tmp/zookeeper_test3", "zookeeper.out")],
  }

def naarad_logs():
  return {
    'zookeeper1': [],
  }


def naarad_config():
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), "naarad.cfg")
