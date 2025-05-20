# MQTT TCP Relay for Gunnerus data livestream

## Using Python

Install packages using pip:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
python mqtt_tcp_relay.py
```

The script reads the data stream from MQTT broker of the Gunnerus and creates a server that listens to TCP connections on port `2947`. The data is then sent to the each TCP client.

You can test the connection using netcat:
```bash
nc localhost 2947
```

## Using Docker

Build the image:
```bash
docker compose up
```

Then test,
```bash
nc localhost 2947
```
