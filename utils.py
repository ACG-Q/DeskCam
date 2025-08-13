import win32gui
import win32con
from PyQt5.QtCore import QRect, QEvent

class UpdateUIEvent(QEvent):
    def __init__(self, callback):
        super().__init__(QEvent.User)
        self.callback = callback

def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        return None
    return QRect(left, top, width, height)

def enum_windows():
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            if rect[2] - rect[0] > 100 and rect[3] - rect[1] > 100:
                windows.append(hwnd)
        return True
    win32gui.EnumWindows(callback, None)
    return windows

def get_window_z_order():
    hwnd = win32gui.GetTopWindow(None)
    order = []
    while hwnd:
        order.append(hwnd)
        hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
    return order


def find_window_under_point(point, exclude_hwnd):
    candidates = []

    def enum_cb(hwnd, _):
        if hwnd == exclude_hwnd:
            return True
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title_len = win32gui.GetWindowTextLength(hwnd)
        if title_len == 0:
            return True
        rect = get_window_rect(hwnd)
        if rect and rect.contains(point[0], point[1]):
            candidates.append(hwnd)
        return True

    win32gui.EnumWindows(enum_cb, None)

    if not candidates:
        return None

    z_order = get_window_z_order()
    for hwnd in z_order:
        if hwnd in candidates:
            return hwnd
    return candidates[0]