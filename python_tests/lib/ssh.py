import cfg
from subprocess import Popen, PIPE

class Cmd:
    def __init__(self,username, host, opts=[]):
        self.ssh_opts = cfg.ssh_opts + opts
        self.username = username
        self.host = host

    def run_script(self, command):
        global failuresReceived
        process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        errorCode = process.returncode
        return stdout,stderr,errorCode

    def run(self, cmd):
        return self.run_script("ssh {} {}@{} '{}'".format(self.opts(), self.username, self.host, cmd))

    def opts(self):
        return " ".join(self.ssh_opts)
