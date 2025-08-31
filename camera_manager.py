import cv2
import requests
import numpy as np
from typing import Optional, Tuple


class CameraManager:
    """
    Handles video input from either a local webcam or a DroidCam HTTP stream.
    """

    def __init__(self):
        self.cap = None
        self.camera_type = "local"          # "local" or "droidcam"
        self.droidcam_url = ""
        self.is_connected = False

    # ------------------------------------------------------------------ #
    # Local webcam
    # ------------------------------------------------------------------ #
    def connect_local_camera(self, camera_index: int = 0) -> bool:
        """Connect to a local webcam."""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if self.cap.isOpened():
                self.camera_type = "local"
                self.is_connected = True
                return True
        except Exception as exc:
            print(f"[CameraManager] Error connecting to local camera: {exc}")

        return False

    # ------------------------------------------------------------------ #
    # DroidCam
    # ------------------------------------------------------------------ #
    def connect_droidcam(self, ip_address: str, port: str = "4747") -> bool:
        """
        Connect to DroidCam using the phone’s IP address.
        Tries several known URL patterns until a valid stream is found.
        """
        url_formats = [
            f"http://{ip_address}:{port}/video",
            f"http://{ip_address}:{port}/mjpegfeed?640x480",
            f"http://{ip_address}:{port}/webcam/stream",
        ]

        for url in url_formats:
            try:
                print(f"[CameraManager] Trying URL: {url}")
                self.cap = cv2.VideoCapture(url)

                # Grab one frame to test the stream
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"[CameraManager] Connected with URL: {url}")
                    self.droidcam_url = url
                    self.camera_type = "droidcam"
                    self.is_connected = True
                    return True

                # Fallback: release and continue to next URL
                self.cap.release()
            except Exception as exc:
                print(f"[CameraManager] Failed with URL {url}: {exc}")
                if self.cap:
                    self.cap.release()

        return False

    def test_droidcam_connection(self, ip_address: str, port: str = "4747") -> bool:
        """
        Quickly verify whether a DroidCam stream is reachable and valid.
        Performs:
            1. HTTP status check
            2. One-frame read through OpenCV
        """
        url_formats = [
            f"http://{ip_address}:{port}/video",
            f"http://{ip_address}:{port}/mjpegfeed?640x480",
        ]

        for url in url_formats:
            try:
                # 1. Simple HTTP check
                rsp = requests.get(url, timeout=3, stream=True)
                if rsp.status_code != 200:
                    continue

                # 2. Can OpenCV read a frame?
                test_cap = cv2.VideoCapture(url)
                ret, frame = test_cap.read()
                test_cap.release()

                if ret and frame is not None and frame.size > 0:
                    print(f"[CameraManager] Connection OK: {url}")
                    return True
            except Exception as exc:
                print(f"[CameraManager] Test failed for {url}: {exc}")

        return False

    # ------------------------------------------------------------------ #
    # Frame retrieval
    # ------------------------------------------------------------------ #
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Return (success_flag, frame).  
        An empty or invalid frame returns (False, None).
        """
        if not self.is_connected or self.cap is None:
            return False, None

        try:
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                # Basic sanity check
                if frame.shape[0] > 0 and frame.shape[1] > 0:
                    return True, frame

            print("[CameraManager] Warning: empty or invalid frame")
            return False, None
        except Exception as exc:
            print(f"[CameraManager] Error reading frame: {exc}")
            return False, None

    # ------------------------------------------------------------------ #
    # House-keeping
    # ------------------------------------------------------------------ #
    def disconnect(self):
        """Release the camera and reset state."""
        if self.cap:
            self.cap.release()
        self.cap = None
        self.is_connected = False
        self.camera_type = "local"
        self.droidcam_url = ""

    def get_camera_info(self) -> dict:
        """Return a dict with current camera details."""
        info = {
            "type": self.camera_type,
            "connected": self.is_connected,
            "url": self.droidcam_url if self.camera_type == "droidcam" else "Local Camera",
        }

        if self.cap and self.is_connected:
            try:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                info.update({"resolution": f"{width}x{height}", "fps": fps})
            except Exception:
                # Some back-ends do not expose all properties
                pass

        return info
