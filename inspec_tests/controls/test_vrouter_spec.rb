#Operating System Check
describe os[:family] do
  it { should eq 'debian' }
end
# Service Check
describe service('acpid') do
  it { should be_enabled }
  it { should be_running }
end
describe service('apparmor') do
  it { should be_running }
end
describe service('atd') do
  it { should be_enabled }
  it { should be_running }
end
describe service('cron') do
  it { should be_enabled }
  it { should be_running }
end
describe service('friendly-recovery') do
  it { should be_enabled }
end
describe service('ntp') do
  it { should be_enabled }
  it { should be_running }
end
describe service('procps') do
  it { should be_enabled }
end
describe service('resolvconf') do
  it { should be_enabled }
  it { should be_running }
end
describe service('rsyslog') do
  it { should be_enabled }
  it { should be_running }
end
describe service('ssh') do
  it { should be_enabled }
  it { should be_running }
end
describe service('sysstat') do
  it { should be_enabled }
  it { should be_running }
end
describe service('udev') do
  it { should be_enabled }
  it { should be_running }
end
docker.containers.running?.ids.each do |id|
  describe docker.object(id) do
    its('State.Health.Status') { should eq 'healthy' }
  end
end
describe docker_container(name: 'vrouter') do
  it { should exist }
  it { should be_running }
end
