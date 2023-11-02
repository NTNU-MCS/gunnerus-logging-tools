# Gunnerus IT Toolbox

- [mqtt tcp relay](mqtt-tcp-relay)

  Reads MQTT stream and publishes NMEA sentences to a TCP socket. Installation instructions are written in its [readme file](mqtt-tcp-relay/README.md).

- [mqtt logger gui](mqtt-logger-gui)

  Utilty tool to log MQTT stream into SQLite database file. It also supports payback.

- [mqtt broker](mqtt-broker)

  MQTT broker with TLS support. It is based on [Eclipse Mosquitto](https://mosquitto.org/). Runs on [docker](https://www.docker.com/). It is designed to be used with [mqtt logger gui](mqtt-logger-gui). While MQTT logger gui playbacks the logged data, this broker is used as the real MQTT broker.