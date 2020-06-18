ARG IMAGE
FROM ${IMAGE}

RUN apk update \
 && apk add \
      g++ \
      pytest

RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --user --upgrade setuptools wheel \
 && python3 -m pip install --user --upgrade python-libsbml

ARG HOME
WORKDIR ${HOME}
