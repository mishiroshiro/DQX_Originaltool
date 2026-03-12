# money_tool.py
# -*- coding: utf-8 -*-
import os, json, time
from datetime import date, timedelta
from PyQt5 import QtWidgets, QtGui, QtCore

# JSONデータ管理クラス
class MoneyData:
    def __init__(self, filepath="money_data.json"):
        self.filepath = filepath
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_income(self, amount, day=None):
        day = day or str(date.today())
        if day not in self.data:
            self.data[day] = []
        self.data[day].append(amount)
        self.save()

    def get_daily_total(self, day=None):
        day = day or str(date.today())
        return sum(self.data.get(day, []))

    def get_last_30_days_totals(self):
        totals = {}
        today = date.today()
        for i in range(30):
            d = today - timedelta(days=i)
            day_str = str(d)
            totals[day_str] = sum(self.data.get(day_str, []))
        return totals

# GUIクラス
class MoneyTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DQ10 金策管理ツール")
        self.setGeometry(200, 100, 600, 700)
        self.setStyleSheet("background-color:#d0f0fd; font-family:'ＭＳ Ｐゴシック'; font-size:11pt;")

        self.data = MoneyData()

        # メインレイアウト
        layout = QtWidgets.QVBoxLayout(self)

        # --- 1回ごとの収入入力 ---
        income_box = QtWidgets.QGroupBox("1回の収入入力")
        income_box.setStyleSheet(self.groupbox_style())
        ib_layout = QtWidgets.QHBoxLayout()
        self.income_input = QtWidgets.QLineEdit()
        self.income_input.setPlaceholderText("収入を入力")
        ib_layout.addWidget(self.income_input)
        btn_add = QtWidgets.QPushButton("追加")
        btn_add.clicked.connect(self.add_income)
        btn_add.setStyleSheet(self.button_style())
        ib_layout.addWidget(btn_add)
        income_box.setLayout(ib_layout)
        layout.addWidget(income_box)

        # --- 今日の合計 ---
        total_box = QtWidgets.QGroupBox("今日の合計")
        total_box.setStyleSheet(self.groupbox_style())
        tb_layout = QtWidgets.QVBoxLayout()
        self.label_total = QtWidgets.QLabel(f"{self.data.get_daily_total()} G")
        self.apply_shadow(self.label_total)
        tb_layout.addWidget(self.label_total)
        total_box.setLayout(tb_layout)
        layout.addWidget(total_box)

        # --- 30日カレンダー表示 ---
        calendar_box = QtWidgets.QGroupBox("過去30日収入カレンダー")
        calendar_box.setStyleSheet(self.groupbox_style())
        cb_layout = QtWidgets.QVBoxLayout()
        self.calendar_view = QtWidgets.QTextEdit()
        self.calendar_view.setReadOnly(True)
        cb_layout.addWidget(self.calendar_view)
        calendar_box.setLayout(cb_layout)
        layout.addWidget(calendar_box)

        # --- 保存・読み込みボタン ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("JSON保存")
        self.save_btn.clicked.connect(self.data.save)
        self.save_btn.setStyleSheet(self.button_style())
        btn_layout.addWidget(self.save_btn)
        self.load_btn = QtWidgets.QPushButton("JSON読み込み")
        self.load_btn.clicked.connect(self.load_data)
        self.load_btn.setStyleSheet(self.button_style())
        btn_layout.addWidget(self.load_btn)
        layout.addLayout(btn_layout)

        self.update_calendar()

    # ---------- スタイル ----------
    def groupbox_style(self):
        return """
            QGroupBox {
                background-color: rgba(255,255,255,230);
                border: 2px solid #80c0ff;
                border-radius: 10px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #d0f8ff, stop:0.5 #a0e0ff, stop:1 #70c0ff);
                border-radius: 6px;
                border: 1px solid #5aa0ff;
                padding: 3px;
            }
            QPushButton:pressed { background-color: #50a0ff; }
        """

    def apply_shadow(self, widget):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(1,1)
        shadow.setColor(QtGui.QColor(128,192,255))
        widget.setGraphicsEffect(shadow)

    # ---------- 機能 ----------
    def add_income(self):
        try:
            amount = int(self.income_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "入力エラー", "数値を入力してください")
            return
        self.data.add_income(amount)
        self.label_total.setText(f"{self.data.get_daily_total()} G")
        self.income_input.clear()
        self.update_calendar()

    def update_calendar(self):
        totals = self.data.get_last_30_days_totals()
        text = "日付\t収入\n"
        for day in sorted(totals.keys(), reverse=True):
            text += f"{day}\t{totals[day]} G\n"
        self.calendar_view.setText(text)

    def load_data(self):
        self.data.load()
        self.label_total.setText(f"{self.data.get_daily_total()} G")
        self.update_calendar()


if __name__=="__main__":
    app = QtWidgets.QApplication([])
    window = MoneyTool()
    window.show()
    app.exec_()