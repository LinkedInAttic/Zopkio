# Copyright 2014 LinkedIn Corp.
#
# This file is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later 
# version.  
#
# This file is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  
#
# See the GNU Lesser General Public License for more details. 
# You may obtain a copy of the License at
# https://www.gnu.org/licenses/lgpl-2.1.html

"""

"""
from contextlib import contextmanager


class DeploymentError(Exception):
  """Represents an exception occurring in the deployment module

  Attributes:
    msg -- explanation of the error
  """

  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return self.msg


class ParamikoError(DeploymentError):
  """Represents an exception if a command Paramiko tries to execute fails

  Attributes:
    msg -- explanation of the error
    errors -- a list of lines representing the output to stderr by paramiko
  """

  def __init__(self, msg, errors):
    self.msg = msg
    self.errors = errors

  def __str__(self):
    return "{0}\n{1}".format(self.msg, self.errors)


def build_os_environment_string(env):
  """ Creates a string of the form export key0=value0;export key1=value1;... for use in
  running commands with the specified environment

  :Parameter variables: a dictionay of environmental variables
  :Returns string: a string that can be prepended to a command to run the command with
  the environmental variables set
  """
  "".join(["export {0}={1}; ".format(key, env[key]) for key in env])

def better_exec_command(ssh, command, msg):
  """Uses paramiko to execute a command but handles failure by raising a ParamikoError if the command fails.
  Note that unlike paramiko.SSHClient.exec_command this is not asynchronous because we wait until the exit status is known

  :Parameter ssh: a paramiko SSH Client
  :Parameter command: the command to execute
  :Parameter msg: message to print on failure

  :Returns (paramiko.Channel)
   the underlying channel so that the caller can extract stdout or send to stdin

  :Raises  SSHException: if paramiko would raise an SSHException
  :Raises  ParamikoError: if the command produces output to stderr
  """
  chan = ssh.get_transport().open_session()
  chan.exec_command(command)
  exit_status = chan.recv_exit_status()
  if exit_status != 0:
    raise ParamikoError(msg, chan.recv_stderr(1024))  # TODO Make this configurable
  return chan


@contextmanager
def open_remote_file(hostname, filename, mode='r', bufsize=-1):
  """

  :param hostname:
  :param filename:
  :return:
  """
  with get_ssh_client(hostname) as ssh:
    sftp = None
    f = None
    try:
      sftp = ssh.open_sftp()
      f = sftp.open(filename, mode, bufsize)
      yield f
    finally:
      if f is not None:
        f.close()
      if sftp is not None:
        sftp.close()


@contextmanager
def get_sftp_client(hostname):
  with get_ssh_client(hostname) as ssh:
    sftp = None
    try:
      sftp = ssh.open_sftp()
      yield sftp
    finally:
      if sftp is not None:
        sftp.close()


@contextmanager
def get_ssh_client(hostname):
  try:
    ssh = sshclient()
    ssh.load_system_host_keys()
    ssh.connect(hostname)
    yield ssh
  finally:
    if ssh is not None:
      ssh.close()

@contextmanager
def get_remote_session(hostname):
  with get_ssh_client(hostname) as ssh:
    try:
      shell = ssh.invoke_shell()
      yield shell
    finally:
      if shell is not None:
        shell.close()

@contextmanager
def get_remote_session_with_environment(hostname, env):
  with get_remote_session(hostname) as shell:
    shell.send(build_os_environment_string(env))
    shell.send("\n")
    yield shell

def sshclient():
  try:
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return ssh
  except ImportError:
    return None