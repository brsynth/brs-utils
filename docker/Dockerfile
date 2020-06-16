FROM python:3-alpine

RUN apk update \
 && apk add \
      gcc \
      musl-dev libffi-dev libressl-dev

RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --user --upgrade setuptools wheel \
 && python3 -m pip install --user --upgrade twine

ARG HOME
WORKDIR ${HOME}
