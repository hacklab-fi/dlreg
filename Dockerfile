FROM debian:buster-slim

MAINTAINER Ville Ranki of Tampere Hacklab

ENV DEBIAN_FRONTEND noninteractive


# Workaround for bug in debian - remove when possible!
RUN mkdir -p /usr/share/man/man1
RUN touch /usr/share/man/man1/sh.distrib.1.gz
# end workaround

RUN apt update
RUN apt -y dist-upgrade
RUN apt -y install python3-pip locales libldap2-dev libsasl2-dev

ADD . /dlreg
WORKDIR /dlreg

RUN pip3 install -r requirements.txt

CMD python3 -u manage.py runserver 0.0.0.0:8000 --noreload

