FROM phusion/passenger-full:0.9.19

MAINTAINER Bitesize Project <bitesize-techops@pearson.com>

CMD ["/sbin/my_init"]

WORKDIR /opt/testexecutor
ENV PATH /opt/testexecutor:$PATH

RUN curl -L -k -s -o get-pip.py https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

RUN apt-get update && apt-get install -y python-dev jq git-all

#Install Python Dependencies
RUN pip install boto3 nose2 botocore python-dateutil PyYaml awscli jwt jmespath s3transfer docutils futures
RUN pip install PyGithub==1.28


#Install INSPEC
RUN gem install inspec

#Install Bats
RUN git clone https://github.com/sstephenson/bats.git && bats/install.sh .

#Install Kubernetes kubectl
RUN curl -L -k -s -o "/opt/testexecutor/kubectl" https://storage.googleapis.com/kubernetes-release/release/v1.2.2/bin/linux/amd64/kubectl

COPY testRunner.py /opt/testexecutor
COPY run.sh /opt/testexecutor

RUN chmod -R 775 /opt/testexecutor/*

ENTRYPOINT ["/opt/testexecutor/run.sh"]
