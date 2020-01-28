FROM python:2-alpine

LABEL maintainer="milonas.ko@gmail.com"
RUN mkdir /app
WORKDIR /app

COPY ./ ./
RUN pip install -e .
RUN mkdir -p /var/log/rabbitmq-alert

CMD ["rabbitmq-alert"]

