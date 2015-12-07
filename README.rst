Zopkio - A Functional and Performance Test Framework for Distributed Systems
============================================================================
  .. image:: https://travis-ci.org/linkedin/Zopkio.svg?branch=master
      :target: https://travis-ci.org/linkedin/Zopkio

  .. image:: https://coveralls.io/repos/linkedin/Zopkio/badge.svg?branch=master&service=github
      :target: https://coveralls.io/github/linkedin/Zopkio?branch=master

Zopkio is a test framework built to support at scale performance and functional
testing.

Installation
------------

Zopkio is distributed via pip

To install::
  (sudo) pip install zopkio

If you want to work with the latest code::

  git clone git@github.com:linkedin/zopkio.git
  cd zopkio

Once you have downloaded the code you can run the zopkio unit tests::

  python setup.py test

Or you can install zopkio and run the sample test::

  (sudo) python setup.py install
  zopkio examples/server_client/server_client.py

N.B the example code assumes you can ssh into your own box using your
ssh keys so if your are having issues with the tests failing check your
authorized_keys.

In the past there have been issues installing one of our dependencies (Naarad)
if you encounter errors installing naarad see
https://github.com/linkedin/naarad/wiki/Installation

Basic usage
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
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Specify the output directory for logs and test results.
                        By default, Zopkio will write to the current directory.
  --log-level LOG_LEVEL
                      Log level (default INFO)
  --console-log-level CONSOLE_LEVEL
                        Console Log level (default ERROR)
  --nopassword          Disable password prompt
  --user USER           user to run the test as (defaults to current user)

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
*deployment_code*. Deplyoment is one of the key features of Zopkio.
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
For each test file, the framework will execute any function with *test* in the
name (no matter the case) and track if the function executes successfully. In
addition if there is a function ``test_foo`` and a function ``validate_foo``,
after all cleanup and log collection is done, if ``test_foo`` executed successfully
then ``validate_foo`` will be executed and tested for successful execution if
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
``naarad_config()``. There are also two functons
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
some of the test configs that zopkio recognizes are:
  * ``loop_all_tests``
  * ``show_all_iterations``
  * ``verify_after_each_test``

'loop_all_tests' repeats the entire test suite for that config for the specified number of times
'show_all_iterations' shows the result in test page for each iteration of the test.
'verify_after_each_test' forces the validation before moving onto the next test

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


Example Tests
-------------
1) command : zopkio examples/server_client/server_client.py

- Runs bunch of tests with multiple clients and servers deployed

2) command : zopkio examples/server_client/single_server_multipleiter_inorder.py --nopassword


- The individual tests have the TEST_PHASE set to be 1,2,3 respectively. This enforces order.
- To run multiple iterations set loop_all_tests to be <value> in config.json file
- To validate each run of the test before moving to next one set verify_after_each_test in configs
- To show the pass/fail for each iteration set show_all_iterations to be true in configs
- sample settings to get mulitple runs for this test
 #. "show_all_iterations":true,
 #. "verify_after_each_test":true,
 #. "loop_all_tests":2,

3) command : zopkio examples/server_client/server_client_multiple_iteration.py

- The base_tests_multiple_iteration.py module has TEST_ITER parameter set to 2.
- This repeats all the tests twice but does not enfore any ordering

4) command : zopkio examples/server_client/client_resilience.py

- This is an example of the test recipe feature of zopkio. See test_recipes.py for recipe and test_resilience.py for example used here
- This tests the kill_recovery recipe to which you pass the deployer, process list, optional restart func, recovery func and timeout
- Zopkio will kill a random process of the deployer and verifies if the system can recover correctly based on recovery function before the timeout value
