FROM phusion/passenger-full:0.9.19

MAINTAINER Bitesize Project <bitesize-techops@pearson.com>

CMD ["/sbin/my_init"]

RUN curl -L -k -s -o get-pip.py https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

RUN apt-get update && apt-get install -y python-dev

#Install Python Dependencies
RUN pip install boto3
RUN pip install nose2
RUN pip install botocore
RUN pip install PyGithub
RUN pip install python-dateutil
RUN pip install PyYaml

#Install INSPEC
RUN gem install inspec

#Install Bats
RUN git clone https://github.com/sstephenson/bats.git
RUN bats/install.sh .
#fpm -s dir -t deb -n bats --iteration $(date "+%Y%m%d%H%M%S") --prefix /usr/local/ bin libexec

RUN mkdir -p var

#Install Kubernetes kubectl
RUN curl -L -k -s -o kubernetes.tar.gz https://github.com/kubernetes/kubernetes/releases/download/v1.2.2/kubernetes.tar.gz
RUN tar -zvxf kubernetes.tar.gz kubernetes/platforms/darwin/amd64/kubectl -C var

#Install Test-Executor run scripts
COPY testRunner.py var
COPY run.sh var

#Cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["/var/run.sh"]
