FROM python:2.7.15-alpine3.7

# yaml-dev 

ADD setup.py setup.py
ADD LICENSE LICENSE
ADD README.md README.md
ADD powerfulseal/ powerfulseal/
RUN apk add --update build-base libffi-dev openssl-dev linux-headers
RUN pip install configparser
RUN python setup.py install 
RUN rm -rf /var/cache/apk/* /tmp/* /var/log/*
