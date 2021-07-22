FROM python:3.8-slim

COPY monitor /monitor

ARG ARTIFACTORY_USER
ARG ARTIFACTORY_TOKEN
ENV PIP_EXTRA_INDEX_URL="https://${ARTIFACTORY_USER}:${ARTIFACTORY_TOKEN}@tr1.jfrog.io/tr1/api/pypi/pypi/simple"

# fetch and install MQ library
RUN apt-get update && apt-get install -y curl && apt-get install -y gcc

RUN mkdir -p /opt/mqm
ENV LD_LIBRARY_PATH="/opt/mqm/lib64:$LD_LIBRARY_PATH"

RUN curl -u "${ARTIFACTORY_USER}":"${ARTIFACTORY_TOKEN}" \
"https://tr1.jfrog.io/artifactory/generic-local/gcs/ibm-mq/9.1.5.0/linux/9.1.5.0-IBM-MQC-Redist-LinuxX64.tar.gz" \
-o mq-lib.tar.gz
RUN tar -xzf mq-lib.tar.gz -C /opt/mqm

# remove unnecessary files from MQ library
RUN rm -rf /opt/mqm/gskit8 /opt/mqm/licenses /opt/mqm/msg /opt/mqm/samp/dotnet

RUN pip install -r monitor/requirements.txt
# Setting this environment variable to something else so the token isn't exposed in the image
ENV PIP_EXTRA_INDEX_URL=empty

CMD python /monitor/initiate_monitor.py