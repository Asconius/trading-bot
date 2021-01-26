FROM python:3.8.1-slim-buster
ARG alphavantage_api_key
ARG from_email_address
ARG to_email_address
ARG email_password
ARG smtp_host
ARG smtp_port

RUN apt-get update
RUN apt-get -y install cron
RUN apt-get -y install curl
RUN apt-get -y install procps
RUN apt-get -y install iputils-ping
RUN apt-get -y install vim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app/database
RUN touch /app/database/tradingbot.db

COPY start.py /app/start.py
COPY src/tradingbot /app/src
COPY templates /app/templates

ENV FLASK_APP=src/main.py
ENV ALPHAVANTAGE_API_KEY=$alphavantage_api_key
ENV FROM_EMAIL_ADDRESS=$from_email_address
ENV TO_EMAIL_ADDRESS=$to_email_address
ENV EMAIL_PASSWORD=$email_password
ENV SMTP_HOST=$smtp_host
ENV SMTP_PORT=$smtp_port

RUN chown 664 /app/database

CMD nohup python start.py & python -m flask run --host=0.0.0.0
