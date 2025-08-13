import threading
import keyboard
from virtual_cam import virtual_cam_loop
from PyQt5.QtWidgets import QApplication
from utils import UpdateUIEvent

class VirtualCameraController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.virtual_cam_thread = None
        self.virtual_cam_running = False

    def start_camera(self, select_rect):
        if not select_rect:
            return

        self.virtual_cam_running = True
        self.virtual_cam_thread = threading.Thread(
            target=self._camera_loop_wrapper, 
            args=(select_rect,),
            daemon=True
        )
        self.virtual_cam_thread.start()

        return True

    def _camera_loop_wrapper(self, select_rect):
        virtual_cam_loop(
            select_rect,
            lambda: self.virtual_cam_running,
            self._on_camera_stop
        )

    def stop_camera(self):
        self.virtual_cam_running = False


    def _on_camera_stop(self):
        app = QApplication.instance()
        app.postEvent(self.main_window, UpdateUIEvent(lambda: self.main_window.show()))

        app.postEvent(self.main_window, UpdateUIEvent(lambda: setattr(self.main_window.btn_start, 'enabled', True)))