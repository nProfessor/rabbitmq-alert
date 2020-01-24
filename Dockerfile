FROM python:2-alpine

LABEL maintainer="milonas.ko@gmail.com"

COPY ./dist ./dist

RUN pip install --no-cache-dir ./dist/rabbitmq-alert-1.8.1.tar.gz

CMD ["rabbitmq-alert"]
