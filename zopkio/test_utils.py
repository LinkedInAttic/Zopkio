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

from datetime import datetime
from datetime import time as dtime
from dateutil import parser
import os
import threading

import zopkio.runtime as runtime


def start_threads_and_join(commands):
  threads = [threading.Thread(target=command) for command in commands]
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()


def get_log_for_test(test_name, log_path, dt_format):
  """
  Gets the portion of the log file relevant to the test (i.e lies between the start and end times of the test).
  It is assumed that every line in the log file starts with a datetime following dtformat.
  :param test_name: the test name
  :param log_path: the absolute path to the log file
  :param dt_format: the format of the datetime in the log file. This could simply be an example datetime because
                   only the word count matters
  """
  word_count = len(dt_format.split())

  start_time = datetime.fromtimestamp(runtime.get_active_test_start_time(test_name))
  end_time = datetime.fromtimestamp(runtime.get_active_test_end_time(test_name))

  start_pos = _search_log_for_datetime(log_path, start_time, word_count)
  end_pos = _search_log_for_datetime(log_path, end_time, word_count, reverse=True)

  with open(log_path, 'r') as log:
    log.seek(start_pos)
    return log.read(end_pos - start_pos)


def _search_log_for_datetime(log_path, dt, word_count, reverse=False):
  """
  Find the start position of the line containing the datetime nearest to dt.
  :param log_path: the absolute path to the log file
  :param dt: the datetime to be searched
  :param word_count: the number of "words" that represents the datetime in the log
  :param reverse: if False, finds the line with the largest datetime less than dt
                  if True, finds the line with the smallest datetime larger than dt
  """
  ONE_KILOBYTE = 1024
  with open(log_path, 'r') as log:
    lbound = 0
    ubound = os.path.getsize(log_path)

    # the algorithm does not guarantee that one of lbound or ubound is changed in each iteration
    # we use search_area to keep track of the block size (ubound - lbound) to see if it changes.
    # It is initialized to 0 in order to declare it before use (note 0 is an impossible case)
    search_area = 0
    while ubound > lbound:
      # Doing a linear search when the size gets small to avoid the issue of keeping track of the previous line.
      if ubound - lbound < ONE_KILOBYTE:
        return _linear_search_log_for_time(log_path, dt, word_count, lbound, ubound, reverse)
      mid = (lbound + ubound) / 2
      log.seek(mid)
      log.readline()  # skip to the end of the line, we will process the next one

      # some lines may not begin with a valid datetime (e.g exception messages that spans multiple lines)
      # hence, we loop until we find a line with a valid datetime
      is_valid_dt = False
      while not is_valid_dt:
        if log.tell() == ubound:
          # we have reached the end of the search block.
          # This should rarely happen unless there is a really long line in the log.
          # Do a linear search because we cannot make further progress
          return _linear_search_log_for_time(log_path, dt, word_count, lbound, ubound, reverse)
        line_start = log.tell()
        line = log.readline()
        timestr = ' '.join(line.split()[:word_count])
        try:
          log_dt = parser.parse(timestr)  # TODO(tlan) exception management
          # if the parse does not work the default time returned is dtime(0, 0, 0)
          # we ignore this time so it is not included in the calculation
          # if a test starts or ends with this time, this will return a superset of the relevant log lines of the tests
          # There may be a chance this affects validation; but the chance is low enough that it is acceptable
          if log_dt.time() != dtime(0, 0, 0):
            is_valid_dt = True
        except:
          is_valid_dt = False

      # the following conditional block updates the bounds. The line that was just process is kept within the bounds,
      # because it still may be the line that we are looking for.
      if log_dt > dt:
        ubound = log.tell()
      elif log_dt < dt:
        lbound = line_start
      else:
        # here we have found a matching time, but we must continue searching
        # because there may be multiple lines with matching times!
        if not reverse:
          ubound = log.tell()
        else:
          lbound = line_start

      #  perform linear search when further progress cannot be made.
      if ubound - lbound == search_area:
        return _linear_search_log_for_time(log_path, dt, word_count, lbound, ubound, reverse)
      search_area = ubound - lbound


def _linear_search_log_for_time(log_path, dt, word_count, lbound, ubound, reverse=False):
  """
  Find the start position of the line containing the datetime nearest to dt.
  :param log_path: the absolute path to the log file
  :param dt: the datetime to be searched
  :param word_count: the number of "words" that represents the datetime in the log
  :param lbound: the byte offset to the start of the block to be searched
  :param ubound: the byte offset to the end of the block to be searched
  :param reverse: if False, finds the line with the largest datetime less than dt
                  if True, finds the line with the smallest datetime larger than dt
  """
  with open(log_path, 'r') as log:
    log.seek(lbound)

    # The following are true at the beginning of each iteration:
    #   - line_start points to the beginning of the line of the datetime we are currently processing
    #   - prev_line_start points the beginning of the previous line (except for the first iteration)
    prev_line_start = lbound
    line_start = log.tell()
    while log.tell() < ubound:
      is_valid_dt = False

      # some lines may not begin with a valid datetime (e.g exception messages that spans multiple lines)
      # hence, we loop until we find a line with a valid datetime
      while not is_valid_dt:
        line = log.readline()
        timestr = ' '.join(line.split()[:word_count])
        try:
          log_dt = parser.parse(timestr)
          is_valid_dt = True
        except:
          is_valid_dt = False
          if log.tell() == ubound:
            if not reverse:
              return prev_line_start
            else:
              return log.tell()

      if not reverse:
        if log_dt >= dt:
          return prev_line_start
        else:
          prev_line_start = line_start
          line_start = log.tell()
          if line_start == ubound:
            # reached the end of block, return the last line
            return prev_line_start
      else:
        if log_dt > dt:
          return log.tell()
        else:
          if log.tell() == ubound:
            # reached the end of block, return the last line
            return log.tell()
          else:
            line_start = log.tell()
