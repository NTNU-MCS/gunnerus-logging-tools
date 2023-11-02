#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import socket
import signal
import threading

class MQTTTCPRelay:
    def __init__(self):
        self.host = 'localhost'
        self.port = 25508
        self.tcp_clients = []
        self.tcp_server = None

        self.mqtt_broker_address = "mqtt.gunnerus.it.ntnu.no"
        self.mqtt_topic = "gunnerus/NMEA/#"
        self.mqtt_client = None

        self.stop = False

        signal.signal(signal.SIGINT, self.__signal_handler)

        self.worker = threading.Thread(target=self.__tcp_server_loop)
        self.worker.start()

        self.__mqtt_client_loop()

    def __mqtt_client_loop(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.mqtt_broker_address)
        self.mqtt_client.on_message = self.__mqtt_callback
        self.mqtt_client.subscribe(self.mqtt_topic)
        self.mqtt_client.loop_start()

    def __tcp_server_loop(self):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.settimeout(1)
        self.tcp_server.bind((self.host, self.port))
        self.tcp_server.listen()

        while not self.stop:
            try:
                client_socket, client_address = self.tcp_server.accept()
            except socket.timeout:
                pass
            else:
                self.tcp_clients.append(client_socket)

    def __broadcast(self, msg):
        for client in self.tcp_clients:
            try:
                client.send(msg.encode())
            except:
                self.tcp_clients.remove(client)

    def __mqtt_callback(self, *args, **kwds):
        _client = args[0]
        _userdata = args[1]
        _message = args[2]

        if len(out := _message.payload.decode().split(" ", 1)) != 2:
            print(f"Invalid message {_message.payload.decode()}")
            return

        timestamp, msg = out

        self.__broadcast(f"{msg}\n")

    def __signal_handler(self, sig, frame):
        self.stop = True

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
