# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, QtGui,QtCore

# ツール読み込み
from tools.kaji_tool import KajiTool
from tools.crystal_tool import CrystalTool
from tools.daily_task_tool import DailyTaskTool
from tools.accessory_tool import AccessoryTool


class MainLauncher(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DQ10 ToolLauncher")
        self.setGeometry(300,150,400,350)

        # 鍛冶ツールと同じ背景
        self.setStyleSheet("""
        background-color:#d0f0fd;
        font-family:'ＭＳ Ｐゴシック';
        font-size:12pt;
        """)

        # アイコン（後で設定）
        # self.setWindowIcon(QtGui.QIcon("icons/25712.ico"))

        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("")
        title.setStyleSheet("font-size:18pt; font-weight:bold;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        from tools.money_tool import MoneyTool

        layout.addWidget(title)

        # ツール保持
        self.open_windows = []

        self.tools = {
            "鍛冶ツール": KajiTool,
            "結晶金策ツール": CrystalTool,
            "日課管理ツール": DailyTaskTool,
            "アクセサリー管理ツール": AccessoryTool,
            "収入管理ツール": MoneyTool

        }

        for name, tool_class in self.tools.items():

            btn = QtWidgets.QPushButton(name)
            btn.setStyleSheet(self.button_style())

            btn.clicked.connect(
                lambda _, cls=tool_class: self.open_tool(cls)
            )

            layout.addWidget(btn)

        self.setLayout(layout)


    def open_tool(self, tool_class):

        window = tool_class()
        window.show()

        self.open_windows.append(window)


    def button_style(self):

        return """
        QPushButton {
            background-color:qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #d0f8ff, stop:0.5 #a0e0ff, stop:1 #70c0ff);
            border-radius:6px;
            border:1px solid #5aa0ff;
            padding:8px;
            font-size:12pt;
        }

        QPushButton:pressed {
            background-color:#50a0ff;
        }
        """


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = MainLauncher()
    window.show()

    sys.exit(app.exec_())