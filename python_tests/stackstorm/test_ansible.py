import os
import sys
import unittest


from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from lib import ssh

class AnsibleTests(unittest.TestCase):
    def setUp(self):
        self.remote = ssh.Cmd('centos', os.getenv("ST2_ADDRESS"))

    def test_no_failures(self):
        cmd = "cat /var/log/cloud-init-output.log | grep -A 2 RECAP | grep -o 'failed=[1-9][0-9]*'"
        stdout,stderr,errorCode = self.remote.run(cmd)
        assert errorCode != 0


if __name__ == "__main__":
    unittest.main(verbosity=2)
