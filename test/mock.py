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
from zopkio.deployer import Deployer, Process
from zopkio import runtime

class Mock_Deployer(Deployer):
    """
    Test stub class to make a concrete class out of abstract Deployer class that does nothing
    """
    def __init__(self):
      super(Mock_Deployer, self).__init__()
      self._proc = None
      self._pid = None

    def __del__(self):
      self.stop("unittest")

    def install(self, unique_id, configs=None):
      pass

    def start(self, unique_id, configs=None):
      import subprocess
      runtime.set_deployer("unittest", self)
      self._proc = subprocess.Popen(["sleep","150"])
      if self._proc is not None:
        self._pid = self._proc.pid
        self.processes[unique_id] = Process(unique_id=unique_id, servicename=unique_id + "-srv", install_path=None, hostname="localhost" )

    def stop(self, unique_id, configs=None):
      if self._proc is not None:
        self._proc.kill()
      if unique_id in self.processes:
        del self.processes[unique_id]
      self._proc = None

    def uninstall(self, unique_id, configs=None):
      pass

    def get_pid(self, unique_id, configs=None):
      return self._proc.pid if self._proc is not None else -1

    def get_host(self, unique_id):
      return "localhost"

    def get_processes(self):
      return self.processes.values()

    def kill_all_process(self):
      pass
