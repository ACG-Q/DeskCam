import os
import json
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QSystemTrayIcon, QMenu, QAction, QApplication
)
from PyQt5.QtGui import QIcon
from ui_components import SquareButton
from PyQt5.QtCore import QRect, Qt
from overlay import Overlay
from utils import UpdateUIEvent
from camera_controller import VirtualCameraController
from config import save_history, load_history

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowTitle("虚拟摄像头桌面区域选择")
        self.setWindowIcon(QIcon('tray_icon.svg'))
        self.setGeometry(100, 100, 300, 200)
        self.select_rect = None
        self.camera_controller = VirtualCameraController(self)

        self.btn_select_window = SquareButton("选择窗口")
        self.btn_free_select = SquareButton("自由选择")
        self.btn_history = SquareButton("历史选择")
        self.btn_start = SquareButton("开启")
        self.btn_start.setEnabled(False)
        self.camera_running = False

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_select_window)
        btn_layout.addWidget(self.btn_free_select)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addWidget(self.btn_start)
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(btn_layout)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.setLayout(layout)

        self.btn_select_window.clicked.connect(self.select_window)
        self.btn_free_select.clicked.connect(self.free_select)
        self.btn_history.clicked.connect(self.load_history)
        self.btn_start.clicked.connect(self.toggle_camera)

        self.init_tray_menu()

    def event(self, event):
        if isinstance(event, UpdateUIEvent):
            event.callback()
            return True
        return super().event(event)

    def select_window(self):
        self.hide()
        self.overlay = Overlay('window_select', self)
        self.overlay.show()

    def free_select(self):
        self.hide()
        self.overlay = Overlay('free_select', self)
        self.overlay.show()

    def load_history(self):
        config_data = load_history()
        if config_data:
            self.select_rect = QRect(config_data['left'], config_data['top'], config_data['width'], config_data['height'])
            self.btn_start.setEnabled(True)
        self.show()

    def toggle_camera(self):
        if not self.select_rect:
            return
        if not self.camera_running:
            self.camera_controller.start_camera(self.select_rect)
            self.btn_start.setText("关闭")
            save_history({
                'top': self.select_rect.top(),
                'left': self.select_rect.left(),
                'width': self.select_rect.width(),
                'height': self.select_rect.height()
            })
            self.camera_running = True
        else:
            self.camera_controller.stop_camera()
            self.btn_start.setText("开启")
            self.camera_running = False

    def init_tray_menu(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('tray_icon.svg'))
        self.tray_icon.setToolTip("虚拟摄像头")
        
        self.tray_menu = QMenu(self)
        
        self.show_action = QAction("显示窗口", self)
        self.show_action.triggered.connect(self.show_normal)
        
        self.quit_action = QAction("退出", self)
        self.quit_action.triggered.connect(self.quit_application)
        
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def show_normal(self):
        self.showNormal()
        self.activateWindow()
    
    def quit_application(self):
        self.close()
        QApplication.quit()
    
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()
    
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "虚拟摄像头",
                "程序已最小化到托盘",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()