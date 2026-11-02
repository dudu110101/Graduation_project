# arduino.py

import serial
import time

from config import (
    ARDUINO_PORT,
    ARDUINO_BAUDRATE
)


class ArduinoController:

    def __init__(self):

        self.port = ARDUINO_PORT
        self.baudrate = ARDUINO_BAUDRATE

        self.serial = None

        self.connect()


    def connect(self):

        try:

            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1
            )

            time.sleep(2)

            print(
                f"[Arduino] Connected: {self.port}"
            )

        except Exception as e:

            print(
                f"[Arduino] Connection failed: {e}"
            )

            self.serial = None


    def send_command(self, command):

        if self.serial is None:
            return False

        try:

            command = command.strip().upper()

            message = command + "\n"

            self.serial.write(
                message.encode("utf-8")
            )

            self.serial.flush()

            print(
                f"[Arduino] Sent: {command}"
            )

            return True

        except Exception as e:

            print(
                f"[Arduino] Send error: {e}"
            )

            return False


    def send_result(self, result):

        result = result.lower()

        if result == "bent":

            return self.send_command(
                "BENT"
            )

        elif result == "missing":

            return self.send_command(
                "MISSING"
            )

        elif result == "solder defect":

            return self.send_command(
                "SOLDER"
            )

        elif result == "good":

            return self.send_command(
                "GOOD"
            )

        return False


    def close(self):

        if self.serial is not None:

            try:
                self.serial.close()

            except Exception:
                pass

            self.serial = None