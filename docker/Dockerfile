
# To build this image:
# sudo docker build -t dlreg-image .

FROM ubuntu

MAINTAINER Ville Ranki

RUN apt-get update

RUN apt-get install -y python-ldap python-django python-passlib git nano

RUN git clone https://github.com/hacklab-fi/dlreg.git

RUN mv dlreg/dlreg/settings_local.py_template dlreg/dlreg/settings_local.py


# To start container,
# sudo docker run --name dlreg -it -p 8887:8000 dlreg-image bash
# nano dlreg/dlreg/settings_local.py
# nano dlreg/dlreg/settings.py    <- Remove DEBUG's if running in production
# exit docker, ctrl-d
# sudo docker start dlreg
# python manage.py runserver 0.0.0.0:8000

