from __future__ import annotations

"""GUI for monitoring technical health and performance of the Cubesat in orbit"""

__author__ = "Elise Katsube"
__version__ = "30/07/26"

import os
import sys
from collections import deque
import receiver

import numpy as np

import pyqtgraph.opengl as gl
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import (
    QWidget, 
    QGridLayout, 
    QApplication,
    QMainWindow, 
    QLabel, 
    QVBoxLayout, 
    QFrame, 
    QMenuBar
 )

CARD_STYLE = """
QFrame {
    background-color: #141B29;
    border-radius: 15px;
    border: 1px solid #27334D;
}
"""

TITLE_STYLE = """
font-size: 18px;
font-weight: bold;
font-family: Arial;
color: #8BE9FD;
"""
VALUE_STYLE = """
font-size: 14px;
color: white;
"""

BATTERY_LEVELS = (
    (50, "#00FF9D", "Normal", "Normal", ""),
    (20, "#FFD166", "Minor Power Saving", "Low Battery Warning", "Reducing non-essential loads"),
    (0, "#FF4D6D", "Severe Power Saving", "Low Battery Critical", "Shutting down non-essential systems"),
)

THERMAL_LEVELS = (
    (15, "#4EA8DE", "Cold Critical", "Super Heating..."),
    (17, "#B866FF", "Cold Warning", "Heating..."),
    (25, "#00FF9D", "Normal", ""),
    (27, "#FFD166", "Heat Warning", "Cooling..."),
    (float("inf"), "#FF4D6D", "Heat Critical", "Super Cooling..."),
)

ORBIT_SCALE = 0.2
ORBIT_TRAIL_MAXLEN = 1200 #300 was no glitches and so was 800
UPDATE_INTERVAL_MS = 100

def battery_level(battery: float):
    """Return (color, mode, status, update_message) for a battery percentage."""
    for threshold, color, mode, status, msg in BATTERY_LEVELS:
        if battery > threshold:
            return color, mode, status, msg
    # Fallback (battery <= lowest threshold, i.e. 0)
    _, color, mode, status, msg = BATTERY_LEVELS[-1]
    return color, mode, status, msg
 
 
def thermal_level(temp_c: float):
    """Return (color, status, update_message) for a temperature in Celsius."""
    for max_temp, color, status, msg in THERMAL_LEVELS:
        if temp_c < max_temp:
            return color, status, msg
    return THERMAL_LEVELS[-1][1:]

def make_image(filename: str, size: int) -> QLabel:
    label = QLabel()
    label.setFixedSize(size, size)
 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pixmap = QPixmap(os.path.join(base_dir, filename))
 
    if not pixmap.isNull():
        label.setPixmap(
            pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
    else:
        label.setText(filename)
        label.setStyleSheet("color:#FF4D6D;")
 
    return label

# ===== CARD WIDGET ===========
class TelemetryCard(QFrame):

    def __init__(self, title, graph, image_type, label):
        super().__init__()

        self.setMinimumSize(250, 200)

        self.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(TITLE_STYLE)
        title_label.setFixedHeight(30)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
        self.value_label = QLabel("No Data")
        self.value_label.setWordWrap(True)
        self.value_label.setFixedHeight(170)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.value_label.setStyleSheet(VALUE_STYLE)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

        layout.setAlignment(title_label, Qt.AlignmentFlag.AlignTop)
        layout.setAlignment(self.value_label, Qt.AlignmentFlag.AlignTop)

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)


        self.orbit_points = deque(maxlen=ORBIT_TRAIL_MAXLEN)
        self.view = None

        self.x = [0,0,0,0,0,0]
        self.y = [0,0,0,0,0,0]


        #initializes a graph
        if graph:
            self.view = gl.GLViewWidget()
            self.view.setCameraPosition(distance=8000)
            self.view.setMinimumHeight(200)
            layout.addWidget(self.view, stretch = 1)
 
            axes = gl.GLAxisItem()
            axes.setSize(6000, 6000, 6000)
            self.view.addItem(axes)

            mesh = gl.MeshData.sphere(rows=30, cols=30, radius=6371 * ORBIT_SCALE)
            earth = gl.GLMeshItem(meshdata=mesh, smooth=True, color=(0.15, 0.55, 0.75, 1), shader="shaded")
            #earth.setGLOptions("translucent")
            self.view.addItem(earth)
 
            self.orbit_line = gl.GLLinePlotItem(
                pos=np.empty((0, 3)), color=(1, 0.4, 1, 1), width=2, antialias=True
            )
            self.view.addItem(self.orbit_line)
 
            self.satellite = gl.GLScatterPlotItem(
                pos=np.array([[0, 0, 0]]), color=(0.3, 0.9, 1.0, 1), size=15
            )
            self.view.addItem(self.satellite)

        self.update_label = QLabel(label)

        if label != None:
            layout.addWidget(self.update_label)

        self.setLayout(layout)

 
    def update_orbit(self, x, y, z):
        self.orbit_points.append((x, y, z))
        points = np.asarray(self.orbit_points)
 
        self.orbit_line.setData(pos=points)
        self.satellite.setData(pos=np.array([[x, y, z]]))
 
    def set_value_style(self, color: str):
        """Apply a colored value-label style, but skip the work (and the
        Qt style re-parse/repaint) if the color hasn't actually changed."""
        if getattr(self, "_last_color", None) == color:
            return
        self._last_color = color
        self.value_label.setStyleSheet(
            f"font-size:14px; font-weight:bold; color:{color};"
        )


# ===== MAIN WINDOW ============
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.updates = deque(maxlen=10)
        self.start_time = datetime.now().strftime("%H:%M:%S")

        self.num_packets = 0
        self._last_packet_id = None  # tracks the last packet object we processed
 
        self.setWindowTitle("CubeSat Dashboard")
        self.setStyleSheet(
            """
            QMainWindow { background-color:#0B0F17; }
            QLabel { color: white; font-size: 14px; }
            """
        )
 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
 
        layout = QGridLayout()
        central_widget.setLayout(layout)
 
        # ------- header ---------------
        header = QLabel("CUBESAT TELEMETRY DASHBOARD")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #00D4FF, stop:0.5 #9D4EDD, stop:1 #00FF9D
            );
            """
        )
        layout.addWidget(header, 0, 1, 1, 5)
 
        # ----------- cards -----------
        self.orbit_card = TelemetryCard("Orbit Position", False, "orbit", None)
        self.power_card = TelemetryCard("Power System", False, "battery", None)
        self.thermal_card = TelemetryCard("Thermal Control", False, "thermo", None)
        self.attitude_card = TelemetryCard("Attitude Control", False, "attitude", None)
        self.update_card = TelemetryCard("Updates", False, "update","Total packets sent:\nStart Time: ")
        self.update_card.value_label.setFixedHeight(306)
        self.update_card.update_label.setFixedHeight(92)

        self.stats_card = TelemetryCard("Orbit Visual", True, "stats", None)
        self.stats_card.setMinimumSize(400, 300) #wxl

        self.stats_card.value_label.hide()
 
        layout.addWidget(self.update_card, 1, 0, 3, 1)

        layout.addWidget(self.orbit_card, 1, 1)
        layout.addWidget(self.power_card, 1, 2)

        layout.addWidget(self.thermal_card, 3, 1)
        layout.addWidget(self.attitude_card, 3, 2)

        layout.addWidget(self.stats_card, 1, 4, 5, 3)

        layout.setColumnStretch(0, 1)   # Updates (thin)
        layout.setColumnStretch(1, 2)   # Orbit position
        layout.setColumnStretch(2, 2)   # Power/Attitude
        layout.setColumnStretch(3, 0)   # empty spacer
        layout.setColumnStretch(4, 5)   # Stats starts here
        layout.setColumnStretch(5, 5)
        layout.setColumnStretch(6, 5)
 
        # ---------- earth image ----------
        earth = make_image("earth.png", 80)
        layout.addWidget(
            earth,
            0,
            0,
            1,
            2,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
 
        # --------------------- Options menu bar ----------------------------------
        menu_bar = QMenuBar()
        menu_bar.setStyleSheet(
            """
            QMenuBar {
                background-color: #0B0F17;
                color: #8dfdcb;
                font-size: 12px;
                font-weight: bold;
            }

            QMenuBar::item {
                padding: 3px 8px;
            }

            QMenuBar::item:selected {
                background-color: #27334D;
            }
            """
        )
 
        option_menu = menu_bar.addMenu("Options")
        option_menu.setStyleSheet("font-weight: bold; color: #45a9a2;")
 
        update_action = QAction("Update", self)
        update_action.setShortcut("Ctrl+U")
 
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
 
        update_action.triggered.connect(self.update_dashboard)
        quit_action.triggered.connect(self.close)
 
        option_menu.addAction(update_action)
        option_menu.addAction(quit_action)
 
        layout.addWidget(
            menu_bar,
            0,
            6,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )
 
        # -------- first update ------------
        self.update_dashboard()
 
        # Timer polls for new telemetry. Actual processing is skipped inside
        # update_dashboard() if the packet hasn't changed since the last tick
        # (see _last_packet_id), so this stays cheap even though it fires
        # every 100ms.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(UPDATE_INTERVAL_MS)

 # ============================ LIVE DATA UPDATE ====================
    def update_dashboard(self):
        if receiver.new_data():
            telemetry = receiver.latest_packet
        else:
            return
 
        packet_type = telemetry.get("packet_type")
        if packet_type == "message request":
            self.update_card.value_label.setText("Received message request...")
            return
        elif packet_type != "telemetry":
            self.update_card.value_label.setText("Waiting for telemetry...")
            return
 
        # Skip reprocessing (and re-rendering) the same packet on every
        # 100ms timer tick when no new telemetry has actually arrived.
        packet_id = id(telemetry)
        if packet_id == self._last_packet_id:
            return
        self._last_packet_id = packet_id
 
        self.num_packets += 1
 
        battery = telemetry["battery_percent"]
 
        position = telemetry["position_km"]
        x, y, z = position["x"], position["y"], position["z"]
 
        temp_c = telemetry["temperature_c"]
        temp_k = temp_c + 273.15
 
        orientation = telemetry["orientation_deg"]
        roll = orientation["roll"]
        pitch = orientation["pitch"]
        yaw = orientation["yaw"]
 
        # ------- ORBIT ----------
        self.orbit_card.value_label.setText(f"X: {x:.1f} km\nY: {y:.1f} km\nZ: {z:.1f} km")
 
        # ------ POWER ---------
        color, power_mode, power_status, power_updates = battery_level(battery)
        self.power_card.set_value_style(color)
        self.power_card.value_label.setText(
            f"Battery: {battery:.1f}%\nMode: {power_mode}\nStatus: {power_status}\n"
        )
 
        # ------- THERMAL ----------
        temp_color, thermal_status, thermal_updates = thermal_level(temp_c)
        self.thermal_card.set_value_style(temp_color)
        self.thermal_card.value_label.setText(
            f"{temp_k:.2f} K\n{temp_c:.2f} °C\nStatus: {thermal_status}"
        )
 
        # ------- UPDATE CARD ----------
        #I want like maximum 6 messages to show, and then it deletes them to show the new ones one at a time
        #I think I'll need a queue
        if thermal_updates:
            self.updates.append(
                f"[{datetime.now():%H:%M:%S}] {thermal_updates}"
            )

        if power_updates:
            self.updates.append(
                f"[{datetime.now():%H:%M:%S}] {power_updates}"
            )

        self.update_card.value_label.setText("\n".join(self.updates))

        self.update_card.update_label.setText(
            f"Total packets sent: {self.num_packets}\nStart Time: {self.start_time}"
        )
 
        # ---------- ATTITUDE ----------
        self.attitude_card.value_label.setText(
            f"Roll: {roll:.1f}°\nPitch: {pitch:.1f}°\nYaw: {yaw:.1f}°"
        )
 
        # --------------- ORBIT TRAIL -----------
        self.stats_card.update_orbit(x * ORBIT_SCALE, y * ORBIT_SCALE, z * ORBIT_SCALE)
 

# =============== RUN APP ===================
if __name__ == "__main__":
    app = QApplication(sys.argv)
 
    window = MainWindow()
    window.show()
 
    sys.exit(app.exec())