ARG IMAGE
FROM ${IMAGE}

ARG FILE
COPY ${FILE}.req .
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --user --upgrade setuptools wheel --no-warn-script-location \
 && python3 -m pip install --no-cache-dir --user --upgrade -r ${FILE}.req

ARG HOME
WORKDIR ${HOME}
