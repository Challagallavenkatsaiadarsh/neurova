# =========================================
# FILE: backend/security/device_fingerprint.py
# =========================================

import platform
import socket
import uuid
import hashlib


class DeviceFingerprint:

    # =========================================
    # GET FULL DEVICE INFO
    # =========================================
    def get_device_info(self):

        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "device_id": self.generate_device_id()
        }

    # =========================================
    # GENERATE UNIQUE DEVICE ID
    # =========================================
    def generate_device_id(self):

        raw_data = (
            platform.system() +
            platform.node() +
            platform.release() +
            platform.processor() +
            socket.gethostname() +
            str(uuid.getnode())
        )

        device_id = hashlib.sha256(
            raw_data.encode()
        ).hexdigest()

        return device_id


# =========================================
# GLOBAL FUNCTION FOR LOGIN SCREEN
# =========================================
def get_device_id():

    fingerprint = DeviceFingerprint()

    return fingerprint.generate_device_id()
