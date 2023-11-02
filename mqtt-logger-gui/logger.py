# This file is part of MQTT Logger.
#
# MQTT LOgger is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# MQTT Logger is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# MQTT Logger. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright: NTNU, 2023
# Author: Emir Cem Gezer, emir.cem.gezer[at]ntnu.no, emircem.gezer[at]gmail.com

import tkinter as tk
from tkinter import filedialog
import time
from pathlib import Path
import mqtt_logger
import toml

class RecorderPlayerApp:
    """
    A simple GUI for recording and playing back MQTT messages.
    """
    def __init__(self, root):
        """
        Initialize the GUI.
        :param root: The root window
        """

        self.root = root
        self.root.title("Recorder and Player")
        self.rec = None

        self.playback = None

        self.configuration = None

        # Buttons
        self.record_button = tk.Button(root, text="Record", command=self.record)
        self.play_button = tk.Button(root, text="Play", command=self.play)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.configure_button = tk.Button(root, text="Configure", command=self.update_config)

        # Layout
        self.play_button.grid(row=0, column=0, padx=10, pady=10)
        self.record_button.grid(row=0, column=1, padx=10, pady=10)
        self.stop_button.grid(row=0, column=2, padx=10, pady=10)
        self.configure_button.grid(row=0, column=4, padx=10, pady=10)

    def update_config(self):
        """
        Update the configuration file. This is done by opening a file dialog
        and selecting a new configuration file. The configuration file is
        expected to be a toml file.
        """
        file_path = filedialog.askopenfilename(
            title="Select a recording file",
            filetypes=[("Toml files", "*.toml")]
        )

        self.configure(config_file=file_path)

    def configure(self, config_file="config.toml"):
        """
        Configure the recorder and player. This is done by reading the config
        file and setting the configuration parameters.
        """

        with open(config_file, "r") as f:
            self.configuration = toml.load(f)

    def record(self):
        """
        Start recording MQTT messages. The messages are stored in a sqlite
        database.
        """
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")

        outdir = Path(self.configuration['recorder']['output_dir']).resolve()
        print(outdir / f"MQTT_log_{timestamp}.db")
        self.rec = mqtt_logger.Recorder(
            sqlite_database_path=(outdir / f"MQTT_log_{timestamp}.db"),
            topics=self.configuration['recorder']["topics"],
            broker_address=self.configuration['recorder']["broker_address"],
            verbose=True
        )

        self.rec.start()
        print(f"Recording started at {timestamp}")

    def play(self):
        """
        Start playing back MQTT messages. The messages are read from a sqlite
        database.
        """
        file_path = filedialog.askopenfilename(title="Select a recording file")
        self.playback = mqtt_logger.Playback(
            sqlite_database_path=file_path,
            broker_address=self.configuration['player']['broker_address'],
            verbose=True
        )

        # Start playback at 1x speed (just as fast)
        self.playback.play(speed=1)

    def stop(self):
        """
        Stop recording MQTT messages.
        """
        if self.rec is not None:
            self.rec.stop()
            self.rec = None



if __name__ == "__main__":
    root = tk.Tk()
    app = RecorderPlayerApp(root)
    app.configure()
    root.mainloop()
