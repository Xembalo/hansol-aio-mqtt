#!/bin/sh

MY_ARGS=""

if [ -n "$ESS_HOST" ]; then
  MY_ARGS="$MY_ARGS --ess_host $ESS_HOST"
fi

if [ -n "$MARIADB_ENABLED" ]; then
  MY_ARGS="$MY_ARGS --mariadb_enabled"
fi

if [ -n "$MARIADB_HOST" ]; then
  MY_ARGS="$MY_ARGS --mariadb_host $MARIADB_HOST"
fi

if [ -n "$MARIADB_PORT" ]; then
  MY_ARGS="$MY_ARGS --mariadb_port $MARIADB_PORT"
fi

if [ -n "$MARIADB_USER" ]; then
  MY_ARGS="$MY_ARGS --mariadb_user $MARIADB_USER"
fi

if [ -n "$MARIADB_PASS" ]; then
  MY_ARGS="$MY_ARGS --mariadb_pass $MARIADB_PASS"
fi

if [ -n "$MARIADB_DATABASE" ]; then
  MY_ARGS="$MY_ARGS --mariadb_database $MARIADB_DATABASE"
fi

if [ -n "$MQTT_ENABLED" ]; then
  MY_ARGS="$MY_ARGS --mqtt_enabled"
fi

if [ -n "$MQTT_CLIENT_IDENTIFIER" ]; then
  MY_ARGS="$MY_ARGS --mqtt_client_identifier $MQTT_CLIENT_IDENTIFIER"
fi

if [ -n "$MQTT_TOPIC" ]; then
  MY_ARGS="$MY_ARGS --mqtt_topic $MQTT_TOPIC"
fi

if [ -n "$MQTT_HOST" ]; then
  MY_ARGS="$MY_ARGS --mqtt_host $MQTT_HOST"
fi

if [ -n "$MQTT_PORT" ]; then
  MY_ARGS="$MY_ARGS --mqtt_port $MQTT_PORT"
fi

if [ -n "$MQTT_QOS" ]; then
  MY_ARGS="$MY_ARGS --mqtt_qos $MQTT_QOS"
fi

exec python3 aio-mqtt.py $MY_ARGS