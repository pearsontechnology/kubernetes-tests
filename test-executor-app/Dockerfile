FROM phusion/passenger-full:0.9.19

MAINTAINER Bitesize Project <bitesize-techops@pearson.com>

WORKDIR /opt/testexecutor
ENV PATH "$PATH:/opt/testexecutor"
ENV PATH "$PATH:/opt/testexecutor/bin"

RUN curl -L -k -s -o get-pip.py https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

RUN apt-get update && apt-get install -y python-dev jq git-all

#Install Python Dependencies
RUN pip install boto3 nose2 botocore python-dateutil PyYaml awscli jwt jmespath s3transfer docutils futures
RUN pip install PyGithub==1.28

#Install INSPEC
RUN gem install --user-install inspec
ENV PATH "$PATH:/root/.gem/ruby/2.3.0/bin"


#Install Bats
RUN git clone https://github.com/sstephenson/bats.git && bats/install.sh .

#Install Kubernetes kubectl
RUN curl -L -k -s -o "/opt/testexecutor/kubectl" https://storage.googleapis.com/kubernetes-release/release/v1.2.2/bin/linux/amd64/kubectl

COPY testRunner.py /opt/testexecutor
COPY run.sh /opt/testexecutor
RUN chmod -R 775 /opt/testexecutor/*

ENTRYPOINT ["/bin/bash","-c","/opt/testexecutor/run.sh"]
