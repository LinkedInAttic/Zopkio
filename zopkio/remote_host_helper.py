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
import errno
import logging
import os
import re
import stat


logger = logging.getLogger(__name__)


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
  return "".join(["export {0}={1}; ".format(key, env[key]) for key in env])

def exec_with_env(ssh, command, msg='', env={}, **kwargs):
  """

  :param ssh:
  :param command:
  :param msg:
  :param env:
  :param synch:
  :return:
  """
  bash_profile_command = "source .bash_profile > /dev/null 2> /dev/null;"
  env_command = build_os_environment_string(env)
  new_command = bash_profile_command + env_command + command
  if kwargs.get('sync', True):
    return better_exec_command(ssh, new_command, msg)
  else:
    return ssh.exec_command(new_command)

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
    msg_str = chan.recv_stderr(1024)
    err_msgs = []
    while len(msg_str) > 0:
      err_msgs.append(msg_str)
      msg_str = chan.recv_stderr(1024)
    err_msg = ''.join(err_msgs)
    logger.error(err_msg)
    raise ParamikoError(msg, err_msg)
  return chan

def log_output(chan):
  """
  logs the output from a remote command
  the input should be an open channel in  the case of synchronous better_exec_command
  otherwise this will not log anything and simply return to the caller
  :param chan:
  :return:
  """
  if hasattr(chan, "recv"):
    str = chan.recv(1024)
    msgs = []
    while len(str) > 0:
      msgs.append(str)
      str = chan.recv(1024)
    msg = ''.join(msgs).strip()
    if len(msg) > 0:
      logger.info(msg)


def copy_dir(ftp, filename, outputdir, prefix, pattern=''):
  """
  Recursively copy a directory flattens the output into a single directory but
  prefixes the files with the path from the original input directory
  :param ftp:
  :param filename:
  :param outputdir:
  :param prefix:
  :param pattern: a regex pattern for files to match (by default matches everything)
  :return:
  """
  try:
    mode = ftp.stat(filename).st_mode
  except IOError, e:
    if e.errno == errno.ENOENT:
      logger.error("Log file " + filename + " does not exist")
      pass
  else:
    if mode & stat.S_IFREG:
      if re.match(pattern, filename) is not None:
        new_file = os.path.join(outputdir, "{0}-{1}".format(prefix, os.path.basename(filename)))
        ftp.get(filename, new_file)
    elif mode & stat.S_IFDIR:
      for f in ftp.listdir(filename):
        copy_dir(ftp, os.path.join(filename, f), outputdir,
                 "{0}_{1}".format(prefix, os.path.basename(filename)), pattern)


@contextmanager
def open_remote_file(hostname, filename, mode='r', bufsize=-1, username=None, password=None):
  """

  :param hostname:
  :param filename:
  :return:
  """
  with get_ssh_client(hostname, username=username, password=password) as ssh:
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
def get_sftp_client(hostname, username=None, password=None):
  with get_ssh_client(hostname, username=username, password=password) as ssh:
    sftp = None
    try:
      sftp = ssh.open_sftp()
      yield sftp
    finally:
      if sftp is not None:
        sftp.close()


@contextmanager
def get_ssh_client(hostname, username=None, password=None):
  try:
    ssh = sshclient()
    ssh.load_system_host_keys()
    ssh.connect(hostname, username=username, password=password)
    yield ssh
  finally:
    if ssh is not None:
      ssh.close()

@contextmanager
def get_remote_session(hostname, username=None, password=None):
  with get_ssh_client(hostname, username=username, password=password) as ssh:
    try:
      shell = ssh.invoke_shell()
      yield shell
    finally:
      if shell is not None:
        shell.close()

@contextmanager
def get_remote_session_with_environment(hostname, env, username=None, password=None):
  with get_remote_session(hostname, username=username, password=password) as shell:
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
