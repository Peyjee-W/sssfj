import sys
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sssfj")
        self.setWindowIcon(QtGui.QIcon('sssfj.ico'))

        self.video_file = 'sssfj.mp4'
        self.cap = cv2.VideoCapture(self.video_file)
        self.lower_threshold = 50
        self.upper_threshold = 150
        self.playing = True
        self.scale_factor = 0.5
        self.playback_speed = 1.0

        self.label = QtWidgets.QLabel(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)

        self.controls_layout = QtWidgets.QHBoxLayout()

        self.btn_pause = QtWidgets.QPushButton("Pause", self)
        self.btn_pause.clicked.connect(self.toggle_play)
        self.controls_layout.addWidget(self.btn_pause)

        self.speed_selector = QtWidgets.QComboBox(self)
        self.speed_selector.addItems(["0.5x", "0.8x", "1.0x", "1.2x", "1.5x", "2.0x", "3.0x"])
        self.speed_selector.currentIndexChanged.connect(self.change_speed)
        self.controls_layout.addWidget(self.speed_selector)

        self.layout.addLayout(self.controls_layout)
        self.setLayout(self.layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.setGeometry(100, 100, 800, 600)
        self.show()

    def update_frame(self):
        if self.playing:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, self.lower_threshold, self.upper_threshold)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_image = np.zeros_like(frame)
            cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
            combined_image = np.hstack((contour_image, frame))

            width = int(combined_image.shape[1] * self.scale_factor)
            height = int(combined_image.shape[0] * self.scale_factor)
            resized_image = cv2.resize(combined_image, (width, height))

            height, width, channel = resized_image.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(resized_image.data, width, height, bytes_per_line, QtGui.QImage.Format_BGR888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(q_image))

    def toggle_play(self):
        self.playing = not self.playing
        self.btn_pause.setText("Resume" if not self.playing else "Pause")

    def change_speed(self):
        speed_mapping = {
            0: 0.5,
            1: 0.8,
            2: 1.0,
            3: 1.2,
            4: 1.5,
            5: 2.0,
            6: 3.0
        }
        self.playback_speed = speed_mapping[self.speed_selector.currentIndex()]
        self.timer.setInterval(int(30 / self.playback_speed))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    sys.exit(app.exec_())
