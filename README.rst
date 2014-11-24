Zopkio - A Functional and Performance Test Framework for Distributed Systems
============================================================================

Zopkio is a test framework built to support at scale performance and functional
testing.

Installation
------------

To install::

  git clone git@github.com:linkedin/distributed-test-framework.git
  cd distributed-test-framework
  sudo python setup.py install

This should install all of the dependencies and allow you to run our sample test::

  zopkio examples/server_client/server_client.py

N.B the example code assumes you can ssh into your own box using your
ssh keys so if your are having issues with the tests failing check your
authorized_keys.

In the past there have been issues installing one of our dependencies (Naarad)
if you encounter errors installing naarad see
https://github.com/linkedin/naarad/wiki/Installation

Basic uasge
-----------

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
-------------------

Zopkio provides the ability to write tests that combine performance and
functional testing across a distributed service or services.
Writing tests using Zopkio should be nearly as simple as writing tests in xUnit
or Nose etc.  A test suite will consist of a single file specifying four
required pieces:

#. A deployment file
#. One or more test files
#. A dynamic configuration file
#. A config directory

For simplicity in the first iteratation this is assumed to be json or a python
file with a dictionary called  *test*.

Deployment
~~~~~~~~~~

The deployment file should be pointed to by an entry in the dictionary called
*deployemnet_code*. Deplyoment is one of the key features of Zopkio.
Developers can write test in
which they bring up arbtrary sets of services on multiple machines and then
within the tests exercise a considerable degree of control over these machines.
The deployment section of code will be similar to deployment in other test
frameworks but because of the increased complexity and the expectation of reuse
across multiple test suites, it can be broken into its own file.

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

In many cases the main task of the deployment code is creating a Deployer.
This can be done using the SSHDeployer provided by the framework or through
custom code. For more information about deployers see the APIs. The ``runtime``
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
times the frameworke will skip tests before autmatically skipping the remaining
tests in that suite.

In addition the entire suite is rerun parameterized by the configurations (See
configs_) there is a second config ``max_suite_failures_before_abort``
which behaves similarly.

Test Files
~~~~~~~~~~

Test files are specified by an entry in the test dictionary called *test_code*,
which should point to a list of test files.
Foreach test file, the framework will execute any function with *test* in the
name and track if the function executes successfully. In addition if there is a
function ``test_foo`` and a function ``validate_foo``, after all cleanup
and log collection is done, if ``test_foo`` executed successfully then
``validate_foo`` will be executed and tested for successful execution if
it fails, the original test will fail and the logs from the post execution will
be displayed. Test can be run in either a parallel mode or a serial mode. By
default tests are run serially without any specified order. However each test file
may specify an attribute *test_phase*. A test_phase of -1 is equivalent to serial
testing. Otherwise all tests with the same test_phase will be run in parallel
together. Phases proceed in ascending order.

Dynamic Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~
The dynamic configuration component may be specified as either
*dynamic_configuration_code* or *perf_code*. This module contains a number
of configurations that can be used during the running of the tests to provide
inputs for the test runner. The required elements are a function to return Naarad
configs, and functions to return the locations of the logs to fetch from the
remote hosts. There are also several configs which can be placed either in this
module as attributes or in the Master config file. The main focus of this module
is support for Naarad. The output of the load
generation can be any format supported by Naarad including JMeter and CSV. The
performacnce file can also contain rules for Naarad to use to pass/fail the
general performance of a run (beyond rules specific to individual tests).  To
get the most from Naarad, a Naarad config file can be provided (see
https://github.com/linkedin/naarad/blob/master/README.md section Usage). In
order to have Naarad support the module should provide a function
``naarad_config(configs, test_name)``. There are also two functons
``machine_logs()`` and ``naarad_logs()`` that should return dictionaries
from ``unique_ids`` to the list of logs to collect.  Machine logs are the
set of logs that should not be processed by naarad.


.. _configs:

Configs
-------

Being able to test with different configurations is extremely important. The
framework distinguishes between three types of configs:

  #. master config
  #. test configs
  #. application configs

Master configs are properties which affect the way zopkio operates. Current properties
that are supported include:
  * ``max_suite_failures_before_abort``
  * ``max_failures_per_suite_before_abort``
  * ``LOGS_DIRECTORY``
  * ``OUTPUT_DIRECTORY``

Test configs are properties which affect how the tests are run. They are specific
to the tests test writer and accessible from
``runtime.get_config(config_name)`` which will return the stored value or the
empty string if no property with that name is present. These are the properties
that can be overrode by the ``config-overrides`` command line flag.

Application configs are properties which affect how the remote services are
configured. There is not currently an official way to copy these configs to remote
hosts separately from the code, although there are several utilities to support it
.

In order to allow the same tests to run over multiple configurations, the
framework interprets configs accoriding to the following rules.  All configs
are grouped under a single folder.  If this folder
contains at least one subfolder, then the config files at the top level are
considered defaults and for each subfolder of the top folder, the entire test
suite will be run using the configs within that folder (plus the defaults and
config overrides). This is the case in which
``max_suite_failures_before_abort`` will be considered. Otherwise the suite
will be run once with the top level config files and overrides.
