ARG PYTHON_VERSION=3.6.7
FROM python:${PYTHON_VERSION}-alpine3.7

RUN mkdir -p /usr/src/app \
    && apk add gcc libffi-dev openssl-dev musl-dev bash
WORKDIR /usr/src/app

COPY requirements.txt install_requires.txt ./

RUN pip install -r requirements.txt

COPY . .


