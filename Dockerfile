FROM oparl/liboparl

ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y python3-pip python3-venv python3-gi redis-server
RUN python3 -m venv /venv && ln -s /usr/lib/python3/dist-packages/gi /venv/lib/python*/site-packages/

ADD . /validator
WORKDIR /validator

RUN /venv/bin/pip install -r requirements.txt

ENTRYPOINT /venv/bin/python validate $0
