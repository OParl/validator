FROM oparl/liboparl

# Set system locale to something sensible (en_US.UTF-8)

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    dpkg-reconfigure locales && \
    /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Install Validator Apt Dependencies

RUN apt update && apt install -y python3-pip python3-gi redis-server

# Provide Validator

ADD . /validator
WORKDIR /validator

# Configure Python Dependencies

RUN pip3 install  -r requirements.txt
RUN service redis-server start

ENTRYPOINT ["./validate"]
