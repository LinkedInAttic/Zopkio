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

from abc import ABCMeta,abstractmethod
import errno
import logging
import os
import signal
import stat
import time

import zopkio.constants as constants
from zopkio.remote_host_helper import better_exec_command, get_sftp_client, get_ssh_client, copy_dir
import zopkio.runtime as runtime

logger = logging.getLogger(__name__)

class Deployer(object):
  """Abstract class specifying required contract for a Deployer

  A deployer implements both the basic contracts for deployment as well as keeping
  track of the state of deployed applications
  """
  __metaclass__ = ABCMeta
  _signalnames = {signal.SIGHUP : "HANGING UP ON",
                  signal.SIGTERM : "TERMINATING",
                  signal.SIGKILL : "KILLING",
                  signal.SIGCONT : "RESUMING",
                  signal.SIGINT : "PAUSING"}

  def __init__(self):
    self.processes = {}

  @abstractmethod
  def install(self, unique_id, configs=None):
    """Install the service. The deployer should use the configs to determine where to install the host

    :Parameter unique_id: the name of the process
    :Parameter configs: a map of configs the deployer may use to determine where to install the service and any
     modifications
    """
    pass

  @abstractmethod
  def start(self, unique_id, configs=None):
    """Start the service.  If `unique_id` has already been installed  it is expected that the service is started on the
    host specified by the previous instance of install.  Otherwise the deployer may use the configs to determine where
    to install the process.

    :Parameter unique_id: the name of the process
    :Parameter configs: a map of configs the deployer may use to modify the start
    """
    pass

  @abstractmethod
  def stop(self, unique_id, configs=None):
    """Stop the service.  If the deployer has not started a service with
    `unique_id` the deployer may take any action.

    :Parameter unique_id: the name of the process
    :Parameter configs: a map of configs the deployer may use to modify the stop
    """
    pass

  def deploy(self, unique_id, configs=None):
    """Deploys the service to the host.  This should at least perform the same actions as install and start
    but may perform additional tasks as needed.

    :Parameter unique_id: the name of the process
    :Parameter configs: a mao of configs the deployer may use to modify the deployment
    """
    self.install(unique_id, configs)
    self.start(unique_id, configs)

  def undeploy(self, unique_id, configs=None):
    """Undeploys the service.  This should at least perform the same actions as stop and uninstall
    but may perform additional tasks as needed.

    :Parameter unique_id: the name of the process
    :Parameter configs: a map of configs the deployer may use
    """
    self.stop(unique_id, configs)
    self.uninstall(unique_id, configs)

  @abstractmethod
  def uninstall(self, unique_id, configs=None):
    """uninstall the service.  If the deployer has not started a service with
    `unique_id` the deployer may take any action. The uninstall is assumed to clean any
    directory the service touches not merely the locations that the service is installed to

    :Parameter unique_id: the name of the process
    :Parameter configs: a map of configs the deployer may use
    """
    pass

  @abstractmethod
  def get_pid(self, unique_id, configs=None):
    """Gets the pid of the process with `unique_id`.  If the deployer does not know of a process
    with `unique_id` then it should return a value of constants.PROCESS_NOT_RUNNING_PID
    If no pid_file/pid_keyword is specified
    a generic grep of ps aux command is executed on remote machine based on process parameters
    which may not be reliable if more process are running with similar name

    :Parameter unique_id: the name of the process
    """
    pass

  @abstractmethod
  def get_host(self, unique_id):
    """Gets the host of the process with `unique_id`.  If the deployer does not know of a process
    with `unique_id` then it should return a value of SOME_SENTINAL_VALUE

    :Parameter unique_id: the name of the process
    """
    pass

  @abstractmethod
  def get_processes(self):
    """ Gets all processes that have been started by this deployer

    :Returns: An iteratable of Processes
    """
    pass

  @abstractmethod
  def kill_all_process(self):
    """ Terminates all the running processes

    """
    pass

  def soft_bounce(self, unique_id, configs=None):
    """ Performs a soft bounce (stop and start) for the specified process

    :Parameter unique_id: the name of the process
    """
    self.stop(unique_id, configs)
    self.start(unique_id, configs)

  def hard_bounce(self, unique_id, configs=None):
    """ Performs a hard bounce (kill and start) for the specified process

    :Parameter unique_id: the name of the process
    """
    self.kill(unique_id, configs)
    self.start(unique_id, configs)

  def sleep(self, unique_id, delay, configs=None):
    """ Pauses the process for the specified delay and then resumes it

    :Parameter unique_id: the name of the process
    :Parameter delay: delay time in seconds
    """
    self.pause(unique_id, configs)
    time.sleep(delay)
    self.resume(unique_id, configs)

  def pause(self, unique_id, configs=None):
    """ Issues a sigstop for the specified process

    :Parameter unique_id: the name of the process
    """
    pids = self.get_pid(unique_id, configs)
    if pids != constants.PROCESS_NOT_RUNNING_PID:
      pid_str = ' '.join(str(pid) for pid in pids)
      hostname = self.processes[unique_id].hostname
      with get_ssh_client(hostname, username=runtime.get_username(), password=runtime.get_password()) as ssh:
        better_exec_command(ssh, "kill -SIGSTOP {0}".format(pid_str), "PAUSING PROCESS {0}".format(unique_id))

  def _send_signal(self, unique_id, signalno, configs):
    """ Issues a signal for the specified process

    :Parameter unique_id: the name of the process
    """
    pids = self.get_pid(unique_id, configs)
    if pids != constants.PROCESS_NOT_RUNNING_PID:
      pid_str = ' '.join(str(pid) for pid in pids)
      hostname = self.processes[unique_id].hostname
      msg=  Deployer._signalnames.get(signalno,"SENDING SIGNAL %s TO"%signalno)
      with get_ssh_client(hostname, username=runtime.get_username(), password=runtime.get_password()) as ssh:
        better_exec_command(ssh, "kill -{0} {1}".format(signalno, pid_str), "{0} PROCESS {1}".format(msg, unique_id))


  def resume(self, unique_id, configs=None):
    """ Issues a sigcont for the specified process

    :Parameter unique_id: the name of the process
    """
    self._send_signal(unique_id, signal.SIGCONT,configs)

  def kill(self, unique_id, configs=None):
    """ Issues a kill -9 to the specified process
    calls the deployers get_pid function for the process. If no pid_file/pid_keyword is specified
    a generic grep of ps aux command is executed on remote machine based on process parameters
    which may not be reliable if more process are running with similar name

    :Parameter unique_id: the name of the process
    """
    self._send_signal(unique_id, signal.SIGKILL, configs)

  def terminate(self, unique_id, configs=None):
    """ Issues a kill -15 to the specified process

    :Parameter unique_id: the name of the process
    """
    self._send_signal(unique_id, signal.SIGTERM, configs)

  def hangup(self, unique_id, configs=None):
    """
    Issue a signal to hangup the specified process

    :Parameter unique_id: the name of the process
    """
    self._send_signal(unique_id, signal.SIGHUP, configs)

  def get_logs(self, unique_id, logs, directory, pattern=constants.FILTER_NAME_ALLOW_NONE):
    """deprecated name for fetch_logs"""
    self.fetch_logs(unique_id, logs, directory, pattern)

  def fetch_logs(self, unique_id, logs, directory, pattern=constants.FILTER_NAME_ALLOW_NONE):
    """ Copies logs from the remote host that the process is running on to the provided directory

    :Parameter unique_id the unique_id of the process in question
    :Parameter logs a list of logs given by absolute path from the remote host
    :Parameter directory the local directory to store the copied logs
    :Parameter pattern a pattern to apply to files to restrict the set of logs copied
    """
    hostname = self.processes[unique_id].hostname
    install_path = self.processes[unique_id].install_path
    self.fetch_logs_from_host(hostname, install_path, unique_id, logs, directory, pattern)

  @staticmethod
  def fetch_logs_from_host(hostname, install_path, prefix, logs, directory, pattern):
    """ Static method Copies logs from specified host on the specified install path

    :Parameter hostname the remote host from where we need to fetch the logs
    :Parameter install_path path where the app is installed
    :Parameter prefix prefix used to copy logs. Generall the unique_id of process
    :Parameter logs a list of logs given by absolute path from the remote host
    :Parameter directory the local directory to store the copied logs
    :Parameter pattern a pattern to apply to files to restrict the set of logs copied
    """
    if hostname is not None:
      with get_sftp_client(hostname, username=runtime.get_username(), password=runtime.get_password()) as ftp:
        for f in logs:
          try:
            mode = ftp.stat(f).st_mode
          except IOError, e:
            if e.errno == errno.ENOENT:
              logger.error("Log file " + f + " does not exist on " + hostname)
              pass
          else:
            copy_dir(ftp, f, directory, prefix)
        if install_path is not None:
          copy_dir(ftp, install_path, directory, prefix, pattern)



class Process(object):
  """
  This is an abstraction of a service installed on a host
  """
  def __init__(self, unique_id, servicename, hostname, install_path):
    """

    :Parameter servicename: the type of service
    :Parameter hostname:  the host that the service is on
    :Parameter alive: if the current process is still alive
    :Parameter unique_id: the name of the process
    """
    self.unique_id = unique_id
    self.servicename = servicename
    self.hostname = hostname
    self.install_path = install_path
    self.start_command = None
    self.args = None
    self.pid_file = None
