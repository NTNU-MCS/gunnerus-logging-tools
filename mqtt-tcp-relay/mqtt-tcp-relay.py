#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import socket
import signal
import threading
import toml
import pynmea2
import time


class MQTTTCPRelay:
    def __init__(self):

        self.mqtt_broker_address = None
        self.mqtt_topics = None
        self.port = None
        self.host = None

        self.__config()

        print(f"Relaying MQTT messages to TCP clients from {self.mqtt_broker_address}")

        self.tcp_clients = []
        self.tcp_server = None
        self.mqtt_client = None
        self.stop = False

        signal.signal(signal.SIGINT, self.__signal_handler)

        self.worker = threading.Thread(target=self.__tcp_server_loop)
        self.worker.start()

        self.__mqtt_client_loop()

    def __mqtt_client_loop(self):
        self.mqtt_client = mqtt.Client()

        while not self.stop:
            try:
                self.mqtt_client.connect(self.mqtt_broker_address)
                print(f"Starting MQTT TCP relay on {self.host}:{self.port}...")
                break
            except ConnectionRefusedError:
                print(f"Connection refused to {self.mqtt_broker_address} retrying in 5 second...")
                time.sleep(5)
                pass

        self.mqtt_client.on_message = self.__mqtt_callback

        for topic in self.mqtt_topics:
            self.mqtt_client.subscribe(topic)

        self.mqtt_client.loop_start()

    def __tcp_server_loop(self):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.settimeout(1)
        self.tcp_server.bind((self.host, self.port))
        self.tcp_server.listen()

        print(f"TCP server listening on {self.host}:{self.port}")
        while not self.stop:
            try:
                client_socket, client_address = self.tcp_server.accept()
                print(f"New client connected {client_address}")
            except socket.timeout:
                pass
            else:
                self.tcp_clients.append(client_socket)

        self.tcp_server.close()

    def __broadcast(self, msg):
        for client in self.tcp_clients:
            try:
                client.send(msg.encode())
            except:
                print(f"Client {client} disconnected")
                self.tcp_clients.remove(client)

    def __mqtt_callback(self, *args, **kwds):
        _client = args[0]
        _userdata = args[1]
        _message = args[2]

        # TODO: This is a custom hack for a specific use case.
        if "NMEA" in _message.topic:
            if len(out := _message.payload.decode().split(" ", 1)) != 2:
                print(f"Invalid message {_message.payload.decode()}")
                return

            timestamp, msg = out
            self.__broadcast(f"{msg}\n")
        elif "SeapathMRU/Heading" in _message.topic:
            heading = _message.payload.decode().split(",")[0]
            nmea_sentence = pynmea2.HDT("GP", "HDT", (heading, "T"))
            self.__broadcast(f"{nmea_sentence}\n")

        elif "SeapathMRU_rates/YawRate" in _message.topic:
            rate = float(_message.payload.decode().split(",")[0])
            rate = rate/60.0
            nmea_sentence = pynmea2.HDT("GP", "ROT", (f"{rate:0,.4f}", "T"))
            self.__broadcast(f"{nmea_sentence}\n")



    def __signal_handler(self, sig, frame):
        print("Stopping MQTT TCP relay...")
        self.stop = True

    def __config(self):
        with open("config.toml", "r") as f:
            config = toml.load(f)

        self.port = config["tcp"]["port"]
        self.host = config["tcp"]["host"]
        self.mqtt_broker_address = config["mqtt"]["broker_address"]
        self.mqtt_topics = config["mqtt"]["topics"]

    def loop(self):
        while True:
            self.worker.join(1)
            if self.stop:
                break


def main():
    relay = MQTTTCPRelay()

    relay.loop()

if __name__ == "__main__":
    main()
