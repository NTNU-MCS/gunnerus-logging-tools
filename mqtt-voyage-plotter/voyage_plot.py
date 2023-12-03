#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os
import pynmea2
import csv

class VoyagePlotter:
    def __init__(self):
        self.db_path = ""

    def read_db(self):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()

        # Get all the NMEA messages that contain the GPS data.
        query = f"""
        SELECT MESSAGE FROM LOG
        WHERE TOPIC LIKE "%NMEA%"
          -- AND MESSAGE LIKE "%$GPGGA%";
        """
        res = curr.execute(query)
        entries = res.fetchall()
        conn.close()

        return entries

    def parse_nmea(self, db_results):
        for row in db_results:

            # Get the NMEA message from the row.
            #
            # b'2023-11-03T09:41:02.769765Z $GPGGA,094102.00,6242.6691,N,00635.6077,E,1,11,0.7,16.6,M,43.0,M,,*5F'
            #   ---------------^----------- -----------------------------------^---------------------------------
            #   Timestamp                   NMEA message

            timestamp = row[0].decode('utf-8').split(' ')[0] # The first element is the timestamp.
            nmea = row[0].decode('utf-8').split(' ')[-1] # The last element is the NMEA message.

            # Check if the message is a NMEA message. The other possibility is
            # that it is an AIS message.
            if nmea[0] != '$':
                continue

            try:
                # Try to parse it
                msg = pynmea2.parse(nmea)
            except pynmea2.nmea.ParseError:
                # Don't care about the failed messages.
                continue

            # Check if the message has the GPS data.
            if not (hasattr(msg, 'latitude') and hasattr(msg, 'longitude')):
                # If it doesn't, skip it.
                continue

            self.add_entry([timestamp, msg.latitude, msg.longitude])


    def add_entry(self, entry):
        # Check if the file exists
        file_exists = os.path.isfile(self.csv_path)

        # Open the CSV file in append mode (create it if it doesn't exist)
        with open(self.csv_path, mode='a', newline='') as csvfile:
            writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL)

            writer.writerow(entry)


    def run(self):
        if len(sys.argv) < 2:
            self.usage()
            sys.exit(1)

        self.db_path = sys.argv[1]
        self.csv_path = sys.argv[2]

        entries = self.read_db()

        self.parse_nmea(entries)

    def usage(self):
        print(f"Usage: {sys.argv[0].split('/')[-1]} <db_path> <csv_path>")



def main():
    plotter = VoyagePlotter()

    plotter.run()

if __name__ == "__main__":
    main()
