#Operating System Check
describe os[:family] do
  it { should eq 'redhat' }
end

# SystemD Service Check
describe service('auditd') do
  it { should be_enabled }
  it { should be_running }
end
describe service('chronyd') do
  it { should be_enabled }
  it { should be_running }
end
describe service('crond') do
  it { should be_enabled }
  it { should be_running }
end
describe service('dbus') do
  it { should be_enabled }
  it { should be_running }
end
describe service('docker') do
  it { should be_enabled }
  it { should be_running }
end
control 'network test' do
  title 'network is running'
  describe.one do
    describe service('calico-node') do
      it { should be_enabled }
      it { should be_running }
    end
    describe service('flanneld') do
      it { should be_enabled }
      it { should be_running }
    end
  end
end
describe service('getty@tty1') do
  it { should be_enabled }
  it { should be_running }
end
describe service('irqbalance') do
  it { should be_enabled }
  it { should be_running }
end
describe service('kubelet') do
  it { should be_enabled }
  it { should be_running }
end
describe service('NetworkManager') do
  it { should be_enabled }
  it { should be_running }
end
describe service('polkit') do
  it { should be_enabled }
  it { should be_running }
end
describe service('rsyslog') do
  it { should be_enabled }
  it { should be_running }
end
describe service('sshd') do
  it { should be_enabled }
  it { should be_running }
end
describe service('systemd-journald') do
  it { should be_enabled }
  it { should be_running }
end
describe service('systemd-logind') do
  it { should be_enabled }
  it { should be_running }
end
describe service('systemd-udevd') do
  it { should be_enabled }
  it { should be_running }
end
describe service('tuned') do
  it { should be_enabled }
  it { should be_running }
end

describe file('/etc/resolv.conf') do
  its('content') { should match(%r{nameserver 172.31.16.2}) }
end
describe file('/etc/ssl/docker-registry.pem') do
  it {should be_file 'docker-registry.pem'}
end
# describe file('/etc/ssl') do
#   its('type') {should match(%r{docker-registry-key.pem}) }
# end
# describe file('/etc/pki/ca-trust/source/anchors') do
#   its('type') {should match(%r{ca.pem}) }
# end
describe file('/etc/hosts') do
  its('content') { should match(%r{172.31.16.3 bitesize-registry.default.svc.cluster.local}) }
end

describe mount('/') do
  it { should be_mounted }
  its('type') { should eq  'xfs' }
end
describe mount('/mnt/ephemeral') do
  it { should be_mounted }
  its('type') { should eq 'ext4'}
end
describe mount('/mnt/docker') do
  it { should be_mounted }
  its('type') { should eq 'btrfs'}
end