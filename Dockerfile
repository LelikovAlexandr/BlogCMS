FROM python:3.8.3
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME=/usr/src/propitanie

RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/log && touch $APP_HOME/log/debug.log
WORKDIR $APP_HOME

COPY . $APP_HOME

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
