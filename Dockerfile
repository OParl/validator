FROM oparl/liboparl

# Install Validator Apt Dependencies

RUN apt update && \
    apt install -y --no-install-recommends \
    python3-pip python3-setuptools python3-gi redis-server && \
    apt autoremove -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "daemonize yes" >> /etc/redis/redis.conf

# Provide Validator

ADD . /validator
WORKDIR /validator

# Configure Python Dependencies

RUN pip3 install  -r requirements.txt
RUN service redis-server start

ENTRYPOINT ["sh", "./docker-validate.sh"]
