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
describe service('consul') do
  it { should be_enabled }
  it { should be_running }
end
describe service('vault') do
  it { should be_enabled }
  it { should be_running }
end
describe port(8500) do
  it { should be_listening }
  its('processes') {should include 'consul'}
end
describe port(8543) do
  it { should be_listening }
  its('processes') {should include 'consul'}
end
describe port(8300) do
  it { should be_listening }
  its('processes') {should include 'consul'}
end
describe port(8400) do
  it { should be_listening }
  its('processes') {should include 'consul'}
end
describe port(8600) do
  it { should be_listening }
  its('processes') {should include 'consul'}
end
describe port(8200) do
  it { should be_listening }
  its('processes') {should include 'vault'}
end
describe port(8243) do
  it { should be_listening }
  its('processes') {should include 'vault'}
end
