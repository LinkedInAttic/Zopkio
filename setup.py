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

"""Zopkio: A distributed testing framework"""

from zopkio import __version__
from setuptools import find_packages, setup
from os import path, listdir

def list_files(directory):
  return [path.join(directory, file)
      for file in listdir(directory)
          if not path.isdir(path.join(directory, file))]

setup(
  name = 'zopkio',
  version = __version__,
  description = __doc__,
  long_description = open('README.rst').read(),
  author = 'Joshua Ehrlich',
  author_email = 'jehrlich@linkedin.com,zopkio@googlegroups.com',
  url = 'http://github.com/linkedin/zopkio',
  download_url = 'https://github.com/linkedin/zopkio/tarball/0.2.5',
  license = 'Apache',
  packages = ['zopkio', 'zopkio.web_resources'],
  package_dir = { 'zopkio' : 'zopkio'},
  package_data = {
    'zopkio' : [
      'web_resources/*.html',
      'web_resources/*.js',
      'web_resources/*.css',
    ]},
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
      'argparse>=1.2.1',
      'numpy>=1.6.2',
      'naarad>=1.0.15',
      'paramiko>=1.10.1',
      'pytz>=2012c',
      'jinja2>=2.7.3',
      'python-dateutil',
      'kazoo>=1.1'
  ],
  entry_points = {
      'console_scripts': [
          'zopkio = zopkio.__main__:main'
      ]
      })
