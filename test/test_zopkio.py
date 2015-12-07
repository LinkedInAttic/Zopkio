import os
import shutil
import unittest
import zopkio.runtime as runtime

class Args:
  def __init__(self):
    self.output_dir = None
    self.log_level = "INFO"
    self.console_level = "INFO"
    self.machine_list = None
    self.config_overrides = None
    self.user = None
    self.password = None
    self.test_list = None
    self.nopassword = True

class TestZopkioMainRunner(unittest.TestCase):
  """
  Test zopkio at an integrated level, running zopkio test suites which
  themselves contain failures and successes and compare expected failured/
  success count at end of zopkio-level integrated test run
  """

  def _run_zopkio(self, args):
    import sys, os.path
    pwd = os.path.abspath('.')
    try:
      os.chdir(os.path.join(os.path.dirname(__file__),".."))
      sys.args = args
      print("Running 'zopkio %s %s'"%(args.testfile, args.nopassword))
      from zopkio import __main__ as main
      succeeded, failed = main.call_main(args)
    except:
      os.chdir( pwd )
      raise
    else:
      return succeeded, failed

  def test_zopkio_launch(self):
    """
    Run server client test suites and
    compare to expected outcome on test failures/successes
    """
    runtime.reset_all()
    args = Args()
    args.testfile = "./examples/server_client/server_client.py"
    succeeded, failed = self._run_zopkio(args)
    self.assertTrue( succeeded >= 4)
    self.assertTrue( failed >= 12)

if __name__ == '__main__':
  unittest.main()
