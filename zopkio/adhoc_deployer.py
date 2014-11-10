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

import logging
import os
import tarfile
import time
import zipfile

import zopkio.constants as constants
from zopkio.deployer import Deployer, Process
from zopkio.remote_host_helper import better_exec_command, DeploymentError, get_sftp_client, get_ssh_client, open_remote_file

logger = logging.getLogger(__name__)

class SSHDeployer(Deployer):
  """
  A simple deployer that copies an executable to the remote host and runs it
  """

  def __init__(self, service_name, configs=None):
    """
    :param service_name: an arbitrary name that can be used to describe the executable
    :param configs: default configurations for the other methods
    :return:
    """
    logging.getLogger("paramiko").setLevel(logging.ERROR)
    self.service_name = service_name
    self.default_configs = {} if configs is None else configs
    Deployer.__init__(self)

  def install(self, unique_id, configs=None):
    """
    Copies the executable to the remote machine under install path. Inspects the configs for te possible keys
    'hostname': the host to install on
    'install_path': the location on the remote host
    'executable': the executable to copy
    'no_copy': if this config is passed in and true then this method will not copy the executable assuming that it is
    already installed

    If the unique_id is already installed on a different host, this will perform the cleanup action first.
    If either 'install_path' or 'executable' are provided the new value will become the default.

    :param unique_id:
    :param configs:
    :return:
    """

    # the following is necessay to set the configs for this function as the combination of the
    # default configurations and the parameter with the parameter superceding the defaults but
    # not modifying the defaults
    if configs is None:
      configs = {}
    tmp = self.default_configs.copy()
    tmp.update(configs)
    configs = tmp

    hostname = None
    if unique_id in self.processes:
      process = self.processes[unique_id]
      prev_hostname = process.hostname
      if 'hostname' in configs:
        if prev_hostname is not configs['hostname']:
          self.uninstall(unique_id, configs)
          hostname = configs['hostname']
        else:
          self.uninstall(unique_id, configs)
          hostname = prev_hostname
    elif 'hostname' in configs:
      hostname = configs['hostname']
    else:
      # we have not installed this unique_id before and no hostname is provided in the configs so raise an error
      logger.error("hostname was not provided for unique_id: " + unique_id)
      raise DeploymentError("hostname was not provided for unique_id: " + unique_id)

    install_path = configs.get('install_path') or self.default_configs.get('install_path')
    if install_path is None:
      logger.error("install_path was not provided for unique_id: " + unique_id)
      raise DeploymentError("install_path was not provided for unique_id: " + unique_id)
    if not configs.get('no_copy', False):
      with get_ssh_client(hostname) as ssh:
        better_exec_command(ssh, "mkdir -p {0}".format(install_path), "Failed to create path {0}".format(install_path))
        better_exec_command(ssh, "chmod a+w {0}".format(install_path), "Failed to make path {0} writeable".format(install_path))
        executable = configs.get('executable') or self.default_configs.get('executable')
        if executable is None:
          logger.error("executable was not provided for unique_id: " + unique_id)
          raise DeploymentError("executable was not provided for unique_id: " + unique_id)
        exec_name = os.path.basename(executable)
        install_location = os.path.join(install_path, exec_name)
        with get_sftp_client(hostname) as ftp:
          ftp.put(executable, install_location)

        # only supports tar and zip (because those modules are provided by Python's standard library)
        if configs.get('extract', False) or self.default_configs.get('extract', False):
          if tarfile.is_tarfile(executable):
            better_exec_command(ssh, "tar -xf {0} -C {1}".format(install_location, install_path), "Failed to extract tarfile {0}".format(exec_name))
          elif zipfile.is_zipfile(executable):
            better_exec_command(ssh, "unzip -o {0} -d {1}".format(install_location, install_path), "Failed to extract zipfile {0}".format(exec_name))
          else:
            logger.error(executable + " is not a supported filetype for extracting")
            raise DeploymentError(executable + " is not a supported filetype for extracting")

    self.processes[unique_id] = Process(unique_id, self.service_name, hostname, install_path)

  def start(self, unique_id, configs=None):
    """
    Start the service.  If `unique_id` has already been installed the deployer will start the service on that host.
    Otherwise this will call install with the configs. Within the context of this function, only four configs are
    considered
    'start_command': the command to run (if provided will replace the default)
    'args': a list of args that can be passed to the command
    'sync': if the command is synchronous or asynchronous defaults to asynchronous
    'delay': a delay in seconds that might be needed regardless of whether the command returns before the service can
    be started

    :param unique_id:
    :param configs:
    :return: if the command is executed synchronously return the underlying paramiko channel which can be used to get the stdout
    otherwise return the triple stdin, stdout, stderr
    """
    # the following is necessay to set the configs for this function as the combination of the
    # default configurations and the parameter with the parameter superceding the defaults but
    # not modifying the defaults
    if configs is None:
      configs = {}
    tmp = self.default_configs.copy()
    tmp.update(configs)
    configs = tmp

    # do not start if already started
    if self.get_pid(unique_id, configs) is not constants.PROCESS_NOT_RUNNING_PID:
      return None

    if unique_id not in self.processes:
      self.install(unique_id, configs)

    hostname = self.processes[unique_id].hostname
    install_path = self.processes[unique_id].install_path

    # order of precedence for start_command and args from highest to lowest:
    # 1. configs
    # 2. from Process
    # 3. from Deployer
    start_command = configs.get('start_command') or self.processes[unique_id].start_command or self.default_configs.get('start_command')
    if start_command is None:
      logger.error("start_command was not provided for unique_id: " + unique_id)
      raise DeploymentError("start_command was not provided for unique_id: " + unique_id)
    args = configs.get('args') or self.processes[unique_id].args or self.default_configs.get('args')
    if args is not None:
      full_start_command = "{0} {1}".format(start_command, ' '.join(args))
    else:
      full_start_command = start_command
    command = "cd {0}; {1}".format(install_path, full_start_command)
    with get_ssh_client(hostname) as ssh:
      if configs.get('sync', False):
        chan = better_exec_command(ssh, command, "Failed to start")
      else:
        chan = ssh.exec_command(command)  # this is a bit weird as chan is a triple of channels but it provides the same semantics as in the synchronous case

    self.processes[unique_id].start_command = start_command
    self.processes[unique_id].args = args

    if 'delay' in configs:
      time.sleep(configs['delay'])
    return chan

  def stop(self, unique_id, configs=None):
    """Stop the service.  If the deployer has not started a service with`unique_id` the deployer will raise an Exception
    There are two configs that will be considered:
    'terminate_only': if this config is passed in then this method is the same as terminate(unique_id) (this is also the
    behvaior if stop_command is None and not overridden)
    'stop_command': overrides the default stop_command

    :param unique_id:
    :param configs:
    :return:
    """
    # the following is necessay to set the configs for this function as the combination of the
    # default configurations and the parameter with the parameter superceding the defaults but
    # not modifying the defaults
    if configs is None:
      configs = {}
    tmp = self.default_configs.copy()
    tmp.update(configs)
    configs = tmp

    if unique_id in self.processes:
      hostname = self.processes[unique_id].hostname
    else:
      logger.error("Can't stop {0}: process not known".format(unique_id))
      raise DeploymentError("Can't stop {0}: process not known".format(unique_id))

    if configs.get('terminate_only', False):
      self.terminate(unique_id, configs)
    else:
      stop_command = configs.get('stop_command') or self.default_configs.get('stop_command')
      if stop_command is not None:
        install_path = self.processes[unique_id].install_path
        with get_ssh_client(hostname) as ssh:
          better_exec_command(ssh, "cd {0}; {1}".format(install_path, stop_command), "Failed to stop {0}".format(unique_id))
      else:
        self.terminate(unique_id, configs)

    if 'delay' in configs:
      time.sleep(configs['delay'])

  def uninstall(self, unique_id, configs=None):
    """uninstall the service.  If the deployer has not started a service with
    `unique_id` this will raise a DeploymentError.  This considers one config:
    'additional_directories': a list of directories to remove in addition to those provided in the constructor plus
     the install path. This will update the directories to remove but does not override it
    :param unique_id:
    :param configs:
    :return:
    """
    # the following is necessay to set the configs for this function as the combination of the
    # default configurations and the parameter with the parameter superceding the defaults but
    # not modifying the defaults
    if configs is None:
      configs = {}
    tmp = self.default_configs.copy()
    tmp.update(configs)
    configs = tmp

    if unique_id in self.processes:
      hostname = self.processes[unique_id].hostname
    else:
      logger.error("Can't uninstall {0}: process not known".format(unique_id))
      raise DeploymentError("Can't uninstall {0}: process not known".format(unique_id))

    install_path = self.processes[unique_id].install_path
    directories_to_remove = self.default_configs.get('directories_to_clean', [])
    directories_to_remove.extend(configs.get('additional_directories', []))
    if install_path not in directories_to_remove:
      directories_to_remove.append(install_path)
    with get_ssh_client(hostname) as ssh:
      for directory_to_remove in directories_to_remove:
        better_exec_command(ssh, "rm -rf {0}".format(directory_to_remove), "Failed to remove {0}".format(directory_to_remove))

  def get_pid(self, unique_id, configs=None):
    """Gets the pid of the process with `unique_id`.  If the deployer does not know of a process
    with `unique_id` then it should return a value of constants.PROCESS_NOT_RUNNING_PID
    """
    RECV_BLOCK_SIZE = 16
    # the following is necessay to set the configs for this function as the combination of the
    # default configurations and the parameter with the parameter superceding the defaults but
    # not modifying the defaults
    if configs is None:
      configs = {}
    tmp = self.default_configs.copy()
    tmp.update(configs)
    configs = tmp

    if unique_id in self.processes:
      hostname = self.processes[unique_id].hostname
    else:
      return constants.PROCESS_NOT_RUNNING_PID

    if self.processes[unique_id].start_command is None:
      return constants.PROCESS_NOT_RUNNING_PID

    if 'pid_file' in configs.keys():
      with open_remote_file(hostname, configs['pid_file']) as pid_file:
        full_output = pid_file.read()
    else:
      pid_keyword = self.processes[unique_id].start_command
      if self.processes[unique_id].args is not None:
        pid_keyword = "{0} {1}".format(pid_keyword, ' '.join(self.processes[unique_id].args))
      pid_keyword = configs.get('pid_keyword', pid_keyword)
      # TODO(jehrlich): come up with a simpler approach to this
      pid_command = "ps aux | grep '{0}' | grep -v grep | tr -s ' ' | cut -d ' ' -f 2 | grep -Eo '[0-9]+'".format(pid_keyword)
      pid_command = configs.get('pid_command', pid_command)
      non_failing_command = "{0}; if [ $? -le 1 ]; then true;  else false; fi;".format(pid_command)
      with get_ssh_client(hostname) as ssh:
        chan = better_exec_command(ssh, non_failing_command, "Failed to get PID")
      output = chan.recv(RECV_BLOCK_SIZE)
      full_output = output
      while len(output) > 0:
        output = chan.recv(RECV_BLOCK_SIZE)
        full_output += output
    if len(full_output) > 0:
      pids = [int(pid_str) for pid_str in full_output.split('\n') if pid_str.isdigit()]
      if len(pids) > 0:
        return pids

    return constants.PROCESS_NOT_RUNNING_PID

  def get_host(self, unique_id):
    """Gets the host of the process with `unique_id`.  If the deployer does not know of a process
    with `unique_id` then it should return a value of SOME_SENTINAL_VALUE

    :Parameter unique_id: the name of the process
    :raises NameError if the name is not  valid process
    """
    if unique_id in self.processes:
      return self.processes[unique_id].hostname
    logger.error("{0} not a known process".format(unique_id))
    raise NameError("{0} not a known process".format(unique_id))

  def get_processes(self):
    """ Gets all processes that have been started by this deployer

    :Returns: A list of Processes
    """
    return self.processes.values()
