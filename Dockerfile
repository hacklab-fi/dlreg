FROM debian:buster-slim

MAINTAINER Ville Ranki of Tampere Hacklab

ENV DEBIAN_FRONTEND noninteractive

RUN apt update
RUN apt upgrade
RUN apt -y install python3-pip locales libldap2-dev libsasl2-dev

ADD . /dlreg
WORKDIR /dlreg

RUN pip3 install -r requirements.txt

CMD python3 manage.py runserver 0.0.0.0:8000

