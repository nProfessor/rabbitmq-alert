FROM python:2-alpine

LABEL maintainer="milonas.ko@gmail.com"

COPY ./dist ./dist
COPY ./rabbitmqalert/config ./dist/config
COPY ./rabbitmqalert/log /var/log/rabbitmq-alert/
COPY ./rabbitmqalert/config /usr/local/lib/python2.7/site-packages/rabbitmqalert/config

RUN pip install --no-cache-dir ./dist/rabbitmq-alert-1.8.1.tar.gz

CMD ["rabbitmq-alert"]

