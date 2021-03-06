FROM registry.access.redhat.com/ubi8/ubi-minimal:latest

RUN microdnf update -y && rm -rf /var/cache/yum
RUN microdnf install python3 git && microdnf clean all

# install python packages
COPY ./requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir && rm requirements.txt

COPY /src /src
COPY /src/license_graph /license_graph
COPY /src/synonyms /synonyms
COPY /src/config.py.template /src/config.py

ADD scripts/entrypoint.sh /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]
