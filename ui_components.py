from PyQt5.QtWidgets import QPushButton

class SquareButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #aaaaaa;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
                border-color: #888888;
            }
        """)