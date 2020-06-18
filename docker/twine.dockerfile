ARG IMAGE
FROM ${IMAGE}

RUN apk update \
 && apk add \
      gcc \
      musl-dev libffi-dev libressl-dev

RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --user --upgrade setuptools wheel --no-warn-script-location \
 && python3 -m pip install --user --upgrade twine

ARG HOME
WORKDIR ${HOME}
