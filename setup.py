#!/usr/bin/env
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

"""DTF: A distributed testing framework"""

from dtf import __version__
from setuptools import find_packages, setup
from os import path, listdir

def list_files(directory):
  return [path.join(directory, file)
      for file in listdir(directory)
          if not path.isdir(path.join(directory, file))]

setup(
  name = 'dtf',
  version = __version__,
  description = __doc__,
  long_description = open('README.rst').read(),
  author = 'Joshua Ehrlich',
  author_email = 'jehrlich@linkedin.com',
  url = 'http://github.com/linkedin/dtf',
  license = 'Apache',
  packages = find_packages(exclude=('test', 'examples')),
  data_files = [
      ('dtf/web_resources/bootstrap/css',
          list_files('dtf/web_resources/bootstrap/css')),
      ('dtf/web_resources/bootstrap/fonts',
          list_files('dtf/web_resources/bootstrap/js')),
      ('dtf/web_resources/bootstrap/js',
          list_files('dtf/web_resources/bootstrap/fonts')),
      ('dtf/web_resources', list_files('dtf/web_resources'))
  ],
  test_suite = 'test',
  classifiers = [
      'Intended Audience :: Developers',
      'License :: OSI Approved :: Apache Software License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
  ],
  install_requires=[
      'argparse',
      'paramiko',
      'nose',
      'numpy',
      'naarad',
      'pytz',
      'jinja2'
  ],
  entry_points = {
      'console_scripts': [
          'dtf = dtf.__main__:main'
      ]
  })
