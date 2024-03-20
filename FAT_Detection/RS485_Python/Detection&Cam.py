from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QPixmap
import cv2
import os
import glob
from pymodbus.client import ModbusSerialClient
import serial
import keyboard
import time

class CamWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cam = cv2.VideoCapture(0)
        self.populate_ui()
        self.frame_count = 0
        self.save_path = "saved_frames"
        os.makedirs(self.save_path, exist_ok=True)

        # Load the face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.save_timer = QtCore.QTimer(self)
        self.save_timer.timeout.connect(self.save_frame)
        self.save_timer.setInterval(1000)  # Interval between saving frames in milliseconds
        self.save_timer.setSingleShot(True)  # Only triggers once

        # Modbus client setup
        self.modbus_client = ModbusSerialClient(method='rtu', port='COM4', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

        self.modbus_timer = QtCore.QTimer(self)
        self.modbus_timer.timeout.connect(self.read_modbus)
        self.modbus_timer.start(100)  # Adjust the interval as needed

    def populate_ui(self):
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setGeometry(10, 10, 640, 480)  # Adjust dimensions as needed

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)  # Adjust frame rate (30 fps in this case)

    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            # Detect faces in the frame
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw rectangles around the detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Display the frame with detected faces
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.image_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_S:
            self.delete_existing_files()
            self.save_frames(5)
            self.frame_count = 0

    def delete_existing_files(self):
        # Delete existing files in the folder
        files = glob.glob(os.path.join(self.save_path, '*'))
        for f in files:
            os.remove(f)

    def save_frames(self, num_frames):
        for _ in range(num_frames):
            self.save_timer.start()
            QtWidgets.QApplication.processEvents()  # Process events to allow GUI updates
            QtCore.QThread.msleep(1000)  # Sleep for 1 second
            self.save_timer.timeout.emit()  # Manually emit the timer timeout signal

    def save_frame(self):
        ret, frame = self.cam.read()
        if ret:
            # Detect faces in the frame
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # Save the frame if a face is detected
            if len(faces) > 0:
                filename = os.path.join(self.save_path, f"frame_{self.frame_count}.png")
                cv2.imwrite(filename, frame)
                self.frame_count += 1

    def closeEvent(self, event):
        self.cam.release()
        event.accept()

    def read_modbus(self):
        if self.modbus_client.connect():
            try:
                result = self.modbus_client.read_holding_registers(0x9C7D, 1, unit=128)
                if not result.isError():
                    print("Holding register value:", result.registers[0])
                    if 200 <= result.registers[0] <= 300:
                        self.delete_existing_files()
                        self.save_frames(5)
                        self.frame_count = 0
            except Exception as e:
                print("Modbus Error:", e)
            finally:
                self.modbus_client.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = CamWidget()
    widget.show()
    app.exec()
