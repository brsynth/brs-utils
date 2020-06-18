ARG IMAGE
FROM ${IMAGE}

RUN apk update \
 && apk add \
      g++ \
      pytest

ARG FILE
COPY ${FILE}.req .
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --user --upgrade setuptools wheel --no-warn-script-location \
 && python3 -m pip install --user --upgrade -r ${FILE}.req

ARG HOME
WORKDIR ${HOME}
