
# To build this image:
# sudo docker build -t dlreg-image .

# To config and start container,

# sudo docker run --name dlreg -it -p 8887:8000 dlreg-image bash
# nano dlreg/dlreg/settings_local.py
# nano dlreg/dlreg/settings.py    <- Remove DEBUG's if running in production
# exit container, ctrl-d
# sudo docker start dlreg
# sudo docker exec -it dlreg python dlreg/manage.py runserver 0.0.0.0:8000

# Regui should be running at http://127.0.0.1:8887



FROM ubuntu

MAINTAINER Ville Ranki

RUN apt-get update

RUN apt-get install -y python-ldap python-django python-passlib git nano

RUN git clone https://github.com/hacklab-fi/dlreg.git

RUN mv dlreg/dlreg/settings_local.py_template dlreg/dlreg/settings_local.py



