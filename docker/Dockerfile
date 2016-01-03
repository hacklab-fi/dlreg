FROM ubuntu

MAINTAINER Ville Ranki

RUN apt-get update

RUN apt-get install -y python-ldap python-django python-passlib git nano

RUN git clone https://github.com/hacklab-fi/dlreg.git

RUN cd dlreg/dlreg

RUN mv settings_local.py_template settings_local.py


# To start container,
# edit settings_local.py

# python manage.py runserver

