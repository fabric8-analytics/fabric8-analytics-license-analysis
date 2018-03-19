FROM centos:7
MAINTAINER Harjindersingh Mistry<hmistry@redhat.com>

RUN yum install -y epel-release && \
    yum install -y python34-setuptools autoconf g++ gcc gcc-c++ glibc-common python34-pip python34-devel && \
    yum clean all

# install python packages
COPY ./requirements.txt /
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY ./src /src
COPY ./tests/license_graph /license_graph
COPY ./tests/synonyms /synonyms
RUN cp /src/config.py.template /src/config.py

ADD scripts/entrypoint.sh /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]

