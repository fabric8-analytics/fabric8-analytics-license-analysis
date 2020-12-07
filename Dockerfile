FROM registry.centos.org/centos/centos:7
MAINTAINER Harjindersingh Mistry<hmistry@redhat.com>

ENV F8A_AUTH_VERSION=fff8f49

RUN yum install -y epel-release && \
    yum install -y python36-setuptools git gcc gcc-c++ python36-pip python36-devel \
    libffi-devel openssl-devel && yum clean all


# install python packages
COPY ./requirements.txt /
RUN pip3 install -r requirements.txt && rm requirements.txt
RUN pip3 install git+https://github.com/fabric8-analytics/fabric8-analytics-auth.git@${F8A_AUTH_VERSION}
COPY ./src /src
COPY ./src/license_graph /license_graph
COPY ./src/synonyms /synonyms
RUN cp /src/config.py.template /src/config.py

ADD scripts/entrypoint.sh /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]

