FROM python:3

ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt -y install libldap2-dev libsasl2-dev

ADD . /dlreg
WORKDIR /dlreg

RUN pip install -r requirements.txt

CMD python -u manage.py runserver 0.0.0.0:8000 --noreload
