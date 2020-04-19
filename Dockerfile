FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir -p /usr/src/propitanine
WORKDIR /usr/src/propitanine

COPY . /usr/src/propitanine

RUN pip install -r requirements.txt
