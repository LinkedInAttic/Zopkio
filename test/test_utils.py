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

import zopkio.utils as utils

class TestUtils(unittest.TestCase):
  FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))

  def test_make_machine_mapping_returns_correct_mapping(self):
    """
    Tests if make_machine_mapping returns the correct mapping
    """
    empty_mapping = utils.make_machine_mapping(None)
    self.assertTrue(type(empty_mapping) is dict)
    self.assertEqual(len(empty_mapping), 0)

    machine_list = ["host1=localhost", "host2=127.0.0.1"]
    machine_mapping = utils.make_machine_mapping(machine_list)
    self.assertEqual(len(machine_mapping), 2)
    self.assertEqual(machine_mapping["host2"], "127.0.0.1")

    self.assertRaises(ValueError, utils.make_machine_mapping,
                      ["host1==localhost"])

  def test_parse_config_list_returns_correct_mapping(self):
    """
    Tests if parse_configs returns the correct mapping
    """
    empty_mapping = utils.parse_config_list(None)
    self.assertTrue(type(empty_mapping) is dict)
    self.assertEqual(len(empty_mapping), 0)

    config_list = ["foo=bar", "a=1"]
    config_mapping = utils.parse_config_list(config_list)
    self.assertEqual(len(config_mapping), 2)
    self.assertEqual(config_mapping["foo"], "bar")

    self.assertRaises(ValueError, utils.parse_config_list, ["a==1"])

  def test_parse_config_file_returns_correct_mapping(self):
    json_mapping = utils.parse_config_file(
        os.path.join(self.FILE_LOCATION, "samples/sample_config.json"))
    self.assertEqual(len(json_mapping), 3)
    self.assertEqual(json_mapping["c"], {'x': 4, 'y': 5, 'z': 6})

    py_mapping = utils.parse_config_file(
        os.path.join(self.FILE_LOCATION, "samples/sample_config.py"))
    self.assertEqual(len(py_mapping), 3)
    self.assertEqual(py_mapping["c"], {'x': 4, 'y': 5, 'z': 6})

    other_mapping = utils.parse_config_file(
        os.path.join(self.FILE_LOCATION, "samples/sample_config"))
    self.assertEqual(len(other_mapping), 3)
    self.assertEqual(other_mapping["a"], '1')

if __name__ == '__main__':
  unittest.main()
