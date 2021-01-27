FROM centos:centos7

RUN yum update -y -q \
    && yum install -y -q gcc  make python36 python3-pip \
    python3-devel  gcc-c++ postgresql-devel postgresql-libs \
    && yum clean all

RUN curl -L https://github.com/edenhill/librdkafka/archive/v0.11.6.tar.gz | tar xzf -
RUN cd librdkafka-0.11.6/ && ./configure --prefix=/usr && make -j && make install

WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app/certs
ENV PYTHONUNBUFFERED=0
VOLUME /usr/src/app/certs

# Bundle app source
COPY . /usr/src/app
RUN  python3 -m pip  install -r requirements.txt





