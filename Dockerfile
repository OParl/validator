FROM ubuntu:17.10
RUN apt-get update
RUN apt install -y valac valadoc gobject-introspection libjson-glib-dev libgirepository1.0-dev meson gettext git

RUN git clone https://github.com/oparl/liboparl
RUN mkdir liboparl/build
WORKDIR /liboparl/build
RUN meson ..
RUN ninja
RUN ninja install
RUN cp OParl-0.2.typelib /usr/lib/x86_64-linux-gnu/girepository-1.0/OParl-0.2.typelib
RUN cd ../..

WORKDIR /
RUN apt install -y python3-pip python3-venv python3-gi
RUN git clone https://github.com/OParl/validator
WORKDIR validator
RUN python3 -m venv venv
RUN ln -s /usr/lib/python3/dist-packages/gi venv/lib/python*/site-packages/
RUN venv/bin/pip install -r requirements.txt

ENTRYPOINT venv/bin/python validate --no-redis $0