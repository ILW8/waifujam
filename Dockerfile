FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip python3-pymysql ca-certificates git

ADD requirements.txt /requirements.txt
MKDIR /waifujam/
WORKDIR /waifujam
RUN python3 -m pip install -r /requirements.txt
COPY . /waifujam
