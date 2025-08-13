from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor
import win32gui
import win32con
import ctypes

from utils import get_window_rect, find_window_under_point

class Overlay(QWidget):
    def __init__(self, mode, main_window):
        super().__init__()
        self.mode = mode  # 'window_select' or 'free_select'
        self.main_window = main_window

        desktop = QApplication.desktop()
        screen_count = desktop.screenCount()
        union_rect = desktop.screenGeometry(0)
        for i in range(1, screen_count):
            union_rect = union_rect.united(desktop.screenGeometry(i))

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(union_rect)

        self.start_pos = None
        self.end_pos = None
        self.selected_rect = None
        self.highlight_hwnd = None
        self.highlight_rect = None
        self.setMouseTracking(True)
        self.show()

        if self.mode == 'window_select':
            self.setCursor(Qt.CrossCursor)
            self.timer = QTimer()
            self.timer.timeout.connect(self.track_mouse_window)
            self.timer.start(16)
        elif self.mode == 'free_select':
            self.setCursor(Qt.CrossCursor)

        hwnd = self.winId().__int__()
        exStyle = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        exStyle &= ~0x20
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, exStyle)


    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()

    def track_mouse_window(self):
        pos = QCursor.pos()
        exclude_hwnd = self.winId().__int__()
        hwnd = find_window_under_point((pos.x(), pos.y()), exclude_hwnd)
        if hwnd != self.highlight_hwnd:
            self.highlight_hwnd = hwnd
            self.highlight_rect = get_window_rect(hwnd) if hwnd else None
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.main_window.show()
            self.close()
            return

        if event.button() == Qt.LeftButton:
            if self.mode == 'window_select':
                pos = QCursor.pos()
                exclude_hwnd = self.winId().__int__()
                hwnd = find_window_under_point((pos.x(), pos.y()), exclude_hwnd)

                if hwnd:
                    self.main_window.select_rect = get_window_rect(hwnd)
                    self.main_window.btn_start.setEnabled(True)

                self.main_window.show()
                self.close()

            elif self.mode == 'free_select':
                self.start_pos = event.pos()
                self.end_pos = event.pos()
                self.update()


    def mouseMoveEvent(self, event):
        if self.mode == 'free_select' and self.start_pos:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == 'free_select' and self.start_pos:
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())

            global_x1 = x1 + self.geometry().left()
            global_y1 = y1 + self.geometry().top()
            width = x2 - x1
            height = y2 - y1
            self.main_window.select_rect = QRect(global_x1, global_y1, width, height)


            self.main_window.btn_start.setEnabled(True)
            self.main_window.show()
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.mode == 'window_select':
            painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
            if self.highlight_rect:
                local_rect = QRect(
                    self.highlight_rect.left() - self.geometry().left(),
                    self.highlight_rect.top() - self.geometry().top(),
                    self.highlight_rect.width(),
                    self.highlight_rect.height()
                )

                painter.fillRect(local_rect, QColor(0, 0, 0, 50))
                pen = QPen(QColor(0, 255, 0, 200), 3)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(local_rect)

        elif self.mode == 'free_select':
            painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
            if self.start_pos and self.end_pos:
                rect = QRect(self.start_pos, self.end_pos)
                painter.fillRect(rect, QColor(0, 255, 255, 50))
                pen = QPen(QColor(0, 255, 255, 180), 3)
                painter.setPen(pen)
                painter.drawRect(rect)
