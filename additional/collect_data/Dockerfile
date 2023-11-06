FROM python:3-alpine

ENV ESS_HOST=
ENV MARIADB_ENABLED=
ENV MARIADB_HOST=
ENV MARIADB_PORT=
ENV MARIADB_USER=
ENV MARIADB_PASS=
ENV MARIADB_DATABASE=
ENV MQTT_ENABLED=
ENV MQTT_CLIENT_IDENTIFIER=
ENV MQTT_TOPIC=
ENV MQTT_HOST=
ENV MQTT_PORT=
ENV MQTT_QOS=

ENV TZ=Europe/Berlin

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY argparser.sh .
COPY qhome.py .
COPY errorcodes.py .

CMD ["./argparser.sh"]