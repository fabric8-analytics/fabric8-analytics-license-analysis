FROM centos:7
MAINTAINER Harjindersingh Mistry<hmistry@redhat.com>

RUN yum install -y epel-release && \
    yum install -y python-pip python-devel gcc && \
    yum clean all


# install python packages
COPY ./requirements.txt /
RUN pip install -r requirements.txt && rm requirements.txt

COPY ./src /src
RUN cp /src/config.py.template /src/config.py

ADD scripts/entrypoint.sh /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]

