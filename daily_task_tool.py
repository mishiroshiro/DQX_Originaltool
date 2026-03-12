# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import datetime
import json
import os

class DailyTaskTool(QtWidgets.QWidget):

    SAVE_FILE = "daily_weekly_task_state.json"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("日課・週課管理ツール")
        self.setGeometry(350, 200, 550, 480)

        # 背景とフォント
        self.setStyleSheet("""
            background-color:#d0f0fd;
            font-family:'ＭＳ Ｐゴシック';
            font-size:12pt;
        """)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # タイトル
        title = QtWidgets.QLabel("日課・週課管理")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:18pt; font-weight:bold; color:#004080;")
        layout.addWidget(title)

        # タブウィジェット
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #5aa0ff;
                border-radius: 8px;
                padding: 5px;
                background: #e0f8ff;
            }
            QTabBar::tab {
                background: #d0f8ff;
                border: 1px solid #5aa0ff;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #70c0ff;
                font-weight:bold;
                color: #002060;
            }
            QTabBar::tab:!selected {
                color: #003080;
            }
        """)
        layout.addWidget(self.tabs)

        # 日課タブ
        self.daily_tab = QtWidgets.QWidget()
        self.daily_layout = QtWidgets.QVBoxLayout()
        self.daily_layout.setSpacing(8)
        self.daily_tab.setLayout(self.daily_layout)
        self.tabs.addTab(self.daily_tab, "日課")

        # 週課タブ
        self.weekly_tab = QtWidgets.QWidget()
        self.weekly_layout = QtWidgets.QVBoxLayout()
        self.weekly_layout.setSpacing(8)
        self.weekly_tab.setLayout(self.weekly_layout)
        self.tabs.addTab(self.weekly_tab, "週課")

        # タスク定義
        self.daily_tasks = [
            "日課1: 日替わり討伐",
            "日課2: 魔因細胞集めと結晶",
            "日課3: 強ボスオーブ回収",
            "日課4: 深淵の咎人"
        ]
        self.weekly_tasks = [
            "週課1: 週替わり討伐真＆偽",
            "週課2: ピラミッドの秘宝",
            "週課3: 万魔の塔",
            "週課4: 試練の門",
            "週課5: 異界アスタルジア",
            "週課6: 源世庫パニガルム",
            "週課7: 達人クエスト"
        ]

        # チェックボックス作成（大きめ、ホバー効果）
        self.daily_checkboxes = []
        for task in self.daily_tasks:
            cb = QtWidgets.QCheckBox(task)
            cb.setStyleSheet(self.checkbox_style())
            cb.stateChanged.connect(self.update_checkbox_style)
            self.daily_layout.addWidget(cb)
            self.daily_checkboxes.append(cb)

        self.weekly_checkboxes = []
        for task in self.weekly_tasks:
            cb = QtWidgets.QCheckBox(task)
            cb.setStyleSheet(self.checkbox_style())
            cb.stateChanged.connect(self.update_checkbox_style)
            self.weekly_layout.addWidget(cb)
            self.weekly_checkboxes.append(cb)

        # ボタンレイアウト
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_reset_daily = QtWidgets.QPushButton("日課リセット")
        self.btn_reset_daily.setStyleSheet(self.button_style())
        self.btn_reset_daily.clicked.connect(self.reset_daily)
        btn_layout.addWidget(self.btn_reset_daily)

        self.btn_reset_weekly = QtWidgets.QPushButton("週課リセット")
        self.btn_reset_weekly.setStyleSheet(self.button_style())
        self.btn_reset_weekly.clicked.connect(self.reset_weekly)
        btn_layout.addWidget(self.btn_reset_weekly)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # 状態管理
        self.task_state = {}
        self.load_state()
        self.auto_reset_if_new_period()
        self.update_checkbox_style()  # 起動時に色反映

    # ボタンスタイル（ホバー効果あり）
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
            QPushButton:hover {
                background-color:#a0e0ff;
            }
            QPushButton:pressed {
                background-color:#50a0ff;
            }
        """

    # チェックボックススタイル
    def checkbox_style(self):
        return """
            QCheckBox {
                font-size:13pt;
                padding:5px;
            }
        """

    # チェック済みはグレー文字に
    def update_checkbox_style(self):
        for cb in self.daily_checkboxes + self.weekly_checkboxes:
            if cb.isChecked():
                cb.setStyleSheet("font-size:13pt; padding:5px; color:gray;")
            else:
                cb.setStyleSheet(self.checkbox_style())

    # 日課リセット
    def reset_daily(self):
        for cb in self.daily_checkboxes:
            cb.setChecked(False)
        self.update_checkbox_style()
        self.save_state()

    # 週課リセット
    def reset_weekly(self):
        for cb in self.weekly_checkboxes:
            cb.setChecked(False)
        self.update_checkbox_style()
        self.save_state()

    # 保存
    def save_state(self):
        data = {
            "date": datetime.date.today().isoformat(),
            "week": datetime.date.today().isocalendar()[1],
            "daily": {cb.text(): cb.isChecked() for cb in self.daily_checkboxes},
            "weekly": {cb.text(): cb.isChecked() for cb in self.weekly_checkboxes}
        }
        with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 読み込み
    def load_state(self):
        if os.path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 日課
                if data.get("date") == datetime.date.today().isoformat():
                    for cb in self.daily_checkboxes:
                        cb.setChecked(data["daily"].get(cb.text(), False))
                # 週課
                if data.get("week") == datetime.date.today().isocalendar()[1]:
                    for cb in self.weekly_checkboxes:
                        cb.setChecked(data["weekly"].get(cb.text(), False))

    # 自動リセット
    def auto_reset_if_new_period(self):
        need_save = False
        if os.path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_date = datetime.date.fromisoformat(data.get("date", datetime.date.today().isoformat()))
                last_week = data.get("week", datetime.date.today().isocalendar()[1])
                if last_date != datetime.date.today():
                    self.reset_daily()
                    need_save = True
                if last_week != datetime.date.today().isocalendar()[1]:
                    self.reset_weekly()
                    need_save = True
        if need_save:
            self.save_state()