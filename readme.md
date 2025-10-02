# Gunnerus Data Logging Toolbox

End-to-end toolbox to log, replay, relay, and visualize ship data over MQTT.

This repository contains:

- mqtt-tcp-relay — Read Kafka-like MQTT topics and relay selected data as NMEA sentences over a TCP socket for client apps (e.g., navigation tools).
- mqtt-logger-gui — Simple Tkinter GUI to record MQTT streams into SQLite and play them back to a broker.
- mqtt-broker — A ready-to-run Eclipse Mosquitto broker configuration (Docker) for local playback/testing.
- mqtt-voyage-plotter — Utility to extract positions from recorded NMEA messages in a DB into a CSV.

You can run the stack with Docker, or run each tool with Python directly.

## Repository structure

- compose.yml — Top-level Compose that includes service Compose files
- mqtt-broker/ — Mosquitto broker config + Compose
- mqtt-tcp-relay/ — MQTT→TCP relay script, config.toml, Dockerfile, Compose
- mqtt-logger-gui/ — Tk GUI app to record/play MQTT logs
- mqtt-voyage-plotter/ — Script to export positions from DB to CSV
- data/ — Example data files

## Prerequisites

- Docker with Docker Compose v2.20+ (for compose include) or specify multiple compose files manually
- Python 3.10+ (recommended 3.11+) if running tools directly
- Git (required because mqtt-logger-gui installs a Git-based dependency)

## Quick start with Docker (broker + relay)

The top-level `compose.yml` includes the broker and the MQTT→TCP relay. This brings up:

- Mosquitto broker on localhost:1883 (and 9001 for websockets)
- TCP relay on localhost:2947, subscribing to configured MQTT topics and broadcasting NMEA sentences to any TCP clients

Steps:

1) Ensure configuration is correct

- Edit `mqtt-tcp-relay/config.toml` if needed:
  - `mqtt.broker_address` default points at `mqtt.gunnerus.it.ntnu.no`. For local playback with the bundled broker, set it to `localhost`.
  - `mqtt.topics` lists all topics to subscribe. Defaults are tailored for Gunnerus data.
  - `tcp.host` and `tcp.port` define where the relay listens (default `0.0.0.0:2947`).

1) Start services

If your Docker Compose supports `include:` in compose files (v2.20+):

```bash
docker compose up --build
```

If your Compose version doesn't support `include:`, run with multiple compose files:

```bash
docker compose -f mqtt-broker/compose.yml -f mqtt-tcp-relay/compose.yml up --build
```

1) Verify

- MQTT broker: Use an MQTT client to publish/subscribe on `localhost:1883`.
- TCP relay: Connect a TCP client and observe NMEA lines, e.g. with netcat:

```bash
# Requires netcat (nc). On some systems the command is `ncat`.
nc localhost 2947
```

Stop with Ctrl+C. To run detached, add `-d` to the compose command.

## Recording and playback with the GUI (Python)

The GUI records MQTT messages into a SQLite database and can play them back to an MQTT broker at adjustable speed.

1) Install dependencies

```bash
python -m venv .venv
# Activate the virtualenv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r mqtt-logger-gui/requirements.txt
```

Notes:

- This installs `mqtt-logger` from GitHub; ensure Git is installed and on PATH.
- Tkinter (Tcl/Tk) may need to be installed depending on your platform:
  - Windows/macOS (python.org installers) typically include Tcl/Tk.
  - Linux may require installing `python3-tk` (e.g., `apt-get install python3-tk`).

1) Configure

The GUI reads `mqtt-logger-gui/config.toml` by default:

```toml
[recorder]
broker_address = "localhost"
topics = ["#"]
output_dir = "data"

[player]
broker_address = "localhost"
topics = ["#/NMEA/#", "#/SeapathMRU/#"]
```

- Set `recorder.broker_address` to your live broker (e.g., `mqtt.gunnerus.it.ntnu.no`) for recording.
- Set `player.broker_address` to the broker you want to publish playback to (often your local Mosquitto at `localhost`).
- `output_dir` is where new DB files will be written during recording.

You can also select a different TOML file at runtime via the Configure button.

1) Run the GUI

```bash
python mqtt-logger-gui/logger.py
```

Actions inside the GUI:

- Record: creates `data/MQTT_log_YYYY-mm-dd-HH-MM-SS.db` under `output_dir` and starts logging the configured topics.
- Play: choose a `.db` file and it will publish messages to the configured broker. UI shows "playing" while active.
- Stop: stops recording or playback gracefully.

## Using the MQTT→TCP relay (Python)

You can also run the relay without Docker.

1) Install dependencies

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r mqtt-tcp-relay/requirements.txt
pip install python-dateutil  # required by the relay but not pinned in the file
```

1) Configure

Edit `mqtt-tcp-relay/config.toml` as described above.

1) Run

```bash
python mqtt-tcp-relay/mqtt-tcp-relay.py --config mqtt-tcp-relay/config.toml
```

1) Test with a TCP client

```bash
nc localhost 2947
```

## Using the local Mosquitto broker only

Run just the broker (useful for GUI playback tests):

```bash
docker compose -f mqtt-broker/compose.yml up --build
```

Ports exposed:

- 1883/tcp (MQTT)
- 9001/tcp (WebSocket MQTT)

Anonymous access is enabled by default in `mqtt-broker/config/mosquitto.conf`; for production, harden the config (users/passwords, ACLs, TLS, etc.).

## Exporting voyage positions to CSV

The utility in `mqtt-voyage-plotter/voyage_plot.py` reads logged DBs and writes a CSV with timestamp, latitude, longitude by parsing NMEA messages.

1) Install dependency

```bash
pip install pynmea2
```

1) Run

```bash
python mqtt-voyage-plotter/voyage_plot.py <path to log>/MQTT_log.db <path to output>/output.csv
```

CSV will be appended to if it already exists.

## License

See `license.txt`. Copyright © NTNU.
