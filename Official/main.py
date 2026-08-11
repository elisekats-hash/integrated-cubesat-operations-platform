"""This is the main function that opens the connection with MQTT, sends packets, receives packets
and opens the GUI"""

from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "28/06/26"

import sys
from PyQt6.QtWidgets import QApplication

import receiver
import telemetry_dashboard

print("Starting receiver...")
receiver.start()

print("Creating QApplication...")
app = QApplication(sys.argv)

print("Creating window...")
window = telemetry_dashboard.MainWindow()

print("Showing window...")
window.show()

print("Entering event loop...")
sys.exit(app.exec())