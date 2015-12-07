ZOPKIO - Distributed performance and functional test framework
===========================================================

A performance and functional test framework for distributed systems.
Please trust the actual source code over the code in the documentation
in the case of conflict. Please point out inconsistencies so that we
can update the docs.

Contents:

.. toctree::
   :maxdepth: 2

Installation
============

Currently the framework is in developement mode and currently is installed in
development mode. The following installation process should work most of the
time but if you have difficulties please open an issue::

  git checkout https://github.com/linkedin/zopkio.git
  cd zopkio
  sudo python setup.py install

This should install all of the dependencies and allow you to run our sample test::

  zopkio examples/server_client/server_client.py

Note that much of the example code assumes you can ssh into your own box using your
ssh keys so if your are having issues with the tests failing check your
authorized_keys.

In the past there have been issues installing one of our dependencies (Naarad)
if you encounter errors installing naarad see
https://github.com/linkedin/naarad/wiki/Installation

If you'd like to see a working test that uses some of the features of the framework
checkout cloud-architecture-evaluator.

Basic uasge
===========

Use the zopkio main script::

  zopkio testfile

Zopkio takes several optional arguments::

  --test-only [TEST_LIST [TEST_LIST ...]]
                        run only the named tests to help debug broken tests
  --machine-list [MACHINE_LIST [MACHINE_LIST ...]]
                        mapping of logical host names to physical names
                        allowing the same test suite to run on different
                        hardware, each argument is a pair of logical name and
                        physical name separated by a =
  --config-overrides [CONFIG_OVERRIDES [CONFIG_OVERRIDES ...]]
                        config overrides at execution time, each argument is a
                        config with its value separated by a =. This has the
                        highest priority of all configs
  --output-dir OUTPUT_DIR
                        Specify the output directory for logs and test results.
                        By default, Zopkio will write to the current directory.

Alternatively you can import zopkio in your code and run specific tests::

  from zopkio.testrunner import TestRunner
  test_runner = TestRunner(testfile, tests, config_overrides)
  test_runner.run()

Testing with Zopkio
================

Zopkio provides the ability to write tests that combine performance and
functional testing across a distributed service or services. The following
examples can be found in zopkio_trunk/src/linkedin/zopkio/test/samples/server_client

Writing tests using Zopkio should be nearly as simple as writing tests in xUnit
or Nose etc.  A test suite will consist of a single file specifying four
required pieces:

#. A deployment file
#. One or more test files
#. One or more perfomance files
#. A config directory

For simplicity in the first iteratation this is assumed to be json or a python
file with a dictionary called  *test* for example see
zopkio_trunk/src/linkedin/zopkio/test/samples/server_client/server_client.py::

  import os
  test = {
    "deployment_code": os.path.join(os.path.dirname(os.path.abspath(__file__)), "deployment.py"),
    "test_code": [os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests.py")],
    "perf_code": os.path.join(os.path.dirname(os.path.abspath(__file__)), "perf.py"),
    "configs_directory": os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs/")
  }

The rest of this document will describe these other files in more detail.

Deployment
----------

Deployment is one of the key features of Zopkio. Developers can write test in
which they bring up arbitrary sets of services on multiple machines and then
within the tests exercise a considerable degree of control over these machines.
The deployment section of code will be similar to deployment in other test
frameworks but because of the increased complexity and the expectation of reuse
across multiple test suites, it can be broken into its own file.

test/samples/server_client/deployment.py::

  import os

  import adhoc_deployer
  import runtime

  server_deployer = None
  client_deployer = None


  def setup_suite():
    client_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "AdditionClient/out/artifacts/AdditionClient_jar/AdditionClient.jar")
    global client_deployer
    client_deployer = adhoc_deployer.SSHDeployer("AdditionClient", "AdditionClient", client_exec,
                                                 start_command="java -jar AdditionClient.jar")
    runtime.set_deployer("AdditionClient", client_deployer)

    client_deployer.install("client1",
                            {"hostname": "localhost",
                             "install_path": "/tmp/server_client/AdditionClients/client1"})

    client_deployer.install("client2",
                            {"hostname": "localhost",
                             "install_path": "/tmp/server_client/AdditionClients/client2"})

    server_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "AdditionServer/out/artifacts/AdditionServer_jar/AdditionServer.jar")
    global server_deployer
    server_deployer = adhoc_deployer.SSHDeployer("AdditionServer", "AdditionServer", server_exec,
                                                 start_command="java -jar AdditionServer.jar")
    runtime.set_deployer("AdditionServer", server_deployer)

    server_deployer.deploy("server1",
                           {"hostname": "localhost",
                            "install_path": "/tmp/server_client/AdditionServers/server1",
                            "args": "localhost 8000".split()})

    server_deployer.deploy("server2",
                           {"hostname": "localhost",
                            "install_path": "/tmp/server_client/AdditionServers/server2",
                            "args": "localhost 8001".split()})

    server_deployer.deploy("server3",
                           {"hostname": "localhost",
                            "install_path": "/tmp/server_client/AdditionServers/server3",
                            "args": "localhost 8002".split()})


  def setup():
    for process in server_deployer.get_processes():
      server_deployer.start(process.unique_id)


  def teardown():
    for process in client_deployer.get_processes():
      client_deployer.stop(process.unique_id)


  def teardown_suite():
    for process in server_deployer.get_processes():
      server_deployer.undeploy(process.unique_id)

A deployment file can contain four functions:

#. ``setup_suite``
#. ``setup``
#. ``teardown``
#. ``teardown_suite``

As in other test frameworks, ``setup_suite`` will run before any of tests,
``setup`` will run before each test, ``teardown`` will run if ``setup`` ran
successfully regardless of the test status, and ``teardown_suite`` will run if
``setup_suite`` ran successfully regardless of any other conditions. The main
distinction in the case of this framework will be in the extended libraries to
support deployment.

In the example during the ``setup_suite`` function the main task is creating a
Deployer (using the SSHDeployer provided by the framework). The ``runtime``
module provides a helpful ``set_deployer(service_name)`` and
``get_deployer(service_name)``.  In addition to allowing the deployers to be
easily shared across functions and modules, using these functions will allow
the framework to automatically handle certain tasks such as copying logs from
the remote hosts.  Once the deployer is created it can be used in both the
setup and teardown functions to start and stop the services.

Since the ``setup`` and ``teardown`` functions run before and after each test a
typical use is to restore the state of the system between tests to prevent
tests from leaking bugs into other tests.  If the ``setup`` or ``teardown``
fails we will skip the test and mark it as a failure. In an effort to avoid
wasting time with a corrupted stack there is a configuration
``max_failures_per_suite_before_abort`` which can be set to determine how many
times we will skip tests before autmatically skipping the remaining tests in
that suite.

In addition the entire suite is rerun parameterized by the configurations (See
:ref:`configs`) there is a second config ``max_suite_failures_before_abort``
which behaves similarly.

Test Files
----------

For each test file, the framework will execute any function with *test* in the
name (no matter the case) and track if the function executes successfully. In
addition if there is a function ``test_foo`` and a function ``validate_foo``,
after all cleanup and log collection is done, if ``test_foo`` executed successfully
then ``validate_foo`` will be executed and tested for successful execution if
it fails, the original test will fail and the logs from the post execution will
be displayed. Consider a simple test with our server client example::

  import os

  import perf
  import runtime


  def test_basic():
    """
    Trivial interaction between client and server
    """
    client_deployer = runtime.get_deployer("AdditionClient")

    client_deployer.start("client1", configs={"args": "localhost 8000 1".split(), "delay": 3})
    client_deployer.start("client1", configs={"args": "localhost 8001 1 2".split(), "delay": 3})
    client_deployer.start("client1", configs={"args": "localhost 8002 1 2 3".split(), "delay": 3})

    client_deployer.start("client2", configs={"args": "localhost 8000 1".split(), "delay": 3})
    client_deployer.start("client2", configs={"args": "localhost 8001 1 2".split(), "delay": 3})
    client_deployer.start("client2", configs={"args": "localhost 8002 1 2 3".split(), "delay": 3})


  def validate_basic():
    """
    Verify the correct sums are received
    """
    with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
      read_data = output.read()
      assert "Received: 1" in read_data, "Did not receive 1 in client1"
      assert "Received: 3" in read_data, "Did not receive 3 in client1"
      assert "Received: 6" in read_data, "Did not receive 6 in client1"

    with open(os.path.join(perf.LOGS_DIRECTORY, "client2-AdditionClient.log")) as output:
      read_data = output.read()
      assert "Received: 1" in read_data, "Did not receive 1 in client2"
      assert "Received: 3" in read_data, "Did not receive 3 in client2"
      assert "Received: 6" in read_data, "Did not receive 6 in client2"


  def test_multi_basic():
    """
    Tests single client multiple runs on same server session
    """
    client_deployer = runtime.get_deployer("AdditionClient")
    server_deployer = runtime.get_deployer("AdditionServer")

    server_deployer.hard_bounce("server1")
    for i in range(0, 3):
      client_deployer.start("client1", configs={"args": "localhost 8000 1 2 3 4".split(), "delay": 3})


  def validate_multi_basic():
    """
    Verify 10 (1+2+3+4) is received 3 times
    """
    with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
      read_data = output.read()
      assert read_data.count("Received: 10") == 2, "Did not receive 10 in client1 2 times"  # fail on purpose


  def test_server_off():
    """
    Tests what happens when trying to connect when the server is off
    """
    client_deployer = runtime.get_deployer("AdditionClient")
    server_deployer = runtime.get_deployer("AdditionServer")

    server_deployer.stop("server1")
    client_deployer.start("client1", configs={"args": "localhost 8000 1 2 3".split(), "delay": 3})


  def validate_server_off():
    """
    Verify that the default error message and a connection refused error message was logged
    """
    with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
      read_data = output.read()
      assert "Addition failed" in read_data, "Did not receive 'Addition failed' in client1"
      assert "Connection refused" in read_data, "Did not receive 'Connection refused' in client1"


  def test_no_valid_ints():
    """
    Tests sending non-integers to the server
    """
    client_deployer = runtime.get_deployer("AdditionClient")
    client_deployer.start("client1", configs={"args": "localhost 8000 a b 3.14".split(), "delay": 3})


  def validate_no_valid_ints():
    """
    Verify 0 is received since no valid integers were sent
    """
    with open(os.path.join(perf.LOGS_DIRECTORY, "client1-AdditionClient.log")) as output:
      assert "Received: 0" in output.read(), "Did not receive 0 in client1"



Performance File
--------------------
Since the installation of load generation is intimately tied to deployment most
of the work is expected to be done there, but there are a few tasks that are
done in this file. The file must contain a map of service names to a list
containing directory where logs and/or data are located and the directory where
the load generation output is located (if desired). The output of the load
generation can be any format supported by Naarad including JMeter and CSV. The
performacnce file can also contain rules for Naarad to use to pass/fail the
general performance of a run (beyond rules specific to individual tests).  To
get the most from Naarad, a Naarad config file can be provided (see
https://github.com/linkedin/naarad/blob/master/README.md section Usage). In
order to have Naarad support the module should provide a function
``naarad_config(configs, test_name)``. There are also two functons
``machine_logs()`` and ``naarad_logs()`` that should return dictionaries
from ``unique_ids`` to the list of logs to collect.  Machine logs are the
set of logs that should not be processed by naarad::

  import os

  LOGS_DIRECTORY = "/tmp/server_client_test/collected_logs/"
  OUTPUT_DIRECTORY = "/tmp/server_client_test/results/"

  def machine_logs():
    return {
    "server1": [os.path.join("/tmp/server_client/AdditionServers/server1", "logs/AdditionServer.log")],
    "server2": [os.path.join("/tmp/server_client/AdditionServers/server2", "logs/AdditionServer.log")],
    "server3": [os.path.join("/tmp/server_client/AdditionServers/server3", "logs/AdditionServer.log")],

    "client1": [os.path.join("/tmp/server_client/AdditionClients/client1", "logs/AdditionClient.log")],
    "client2": [os.path.join("/tmp/server_client/AdditionClients/client2", "logs/AdditionClient.log")],
  }

  def naarad_logs():
    return {
    "server1": [os.path.join("/tmp/server_client/AdditionServers/server1", "logs/AdditionServerPerf.csv")],
    "server2": [os.path.join("/tmp/server_client/AdditionServers/server2", "logs/AdditionServerPerf.csv")],
    "server3": [os.path.join("/tmp/server_client/AdditionServers/server3", "logs/AdditionServerPerf.csv")],

    "client1": [os.path.join("/tmp/server_client/AdditionClients/client1", "logs/AdditionClientPerf.csv")],
    "client2": [os.path.join("/tmp/server_client/AdditionClients/client2", "logs/AdditionClientPerf.csv")],
  }


  def naarad_config(config, test_name=None):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "naarad.cfg")


.. _configs:

Configs
-------

Being able to test with different configurations is extremely important. The
framework distinguishes between three types of configs:

  #. master config
  #. test configs
  #. application configs

Master configs are properties which affect the way zopkio operates. Current properties
that are supported include ``max_suite_failures_before_abort`` and
``max_failures_per_suite_before_abort``.


Test configs are properties which affect how the tests are run. They are specific
to the tests test writer and accessible from
``runtime.get_config(config_name)`` which will return the stored value or the
empty string if no property with that name is present. These are the properties
that can be overridden by the ``config-overrides`` command line flag.

Application configs are properties which affect how the remote services are
configured, there is not currently a decision as to how we will install these
configurations on the remote hosts.

In order to allow the same tests to run over multiple configurations, the
framework interprets configs accoriding to the following rules.  All configs
are grouped under a single folder test/samples/server_client/configs.  If this folder
contains at least one subfolder, then the config files at the top level are
considered defaults and for each subfolder of the top folder, the entire test
suite will be run using the configs within that folder (plus the defaults and
config overrides). This is the case in which
``max_suite_failures_before_abort`` will be considered. Otherwise the suite
will be run once with the top level config files and overrides.
