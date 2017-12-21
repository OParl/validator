#!/usr/bin/env sh

nohup redis-server /etc/redis/redis.conf &
./validate $@
