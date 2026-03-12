# -*- coding: utf-8 -*-
import csv
from PyQt5 import QtWidgets, QtCore, QtGui

class AccessoryTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DQ10 アクセサリー管理ツール")
        self.setGeometry(300, 150, 700, 500)
        self.setStyleSheet("background-color:#d0f0fd; font-family:'ＭＳ Ｐゴシック'; font-size:11pt;")
        self.accessories = []

        self.initUI()
        self.refresh_table()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        # --- タイトル ---
        title = QtWidgets.QLabel("アクセサリー管理ツール")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:18pt; font-weight:bold;")
        layout.addWidget(title)

        # --- テーブル ---
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["名前", "取得", "効果1", "効果2", "効果3"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # --- 収集率 ---
        progress_box = QtWidgets.QGroupBox("収集率")
        progress_box.setStyleSheet(self.groupbox_style())
        vbox = QtWidgets.QVBoxLayout()
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("収集率: %p%")
        vbox.addWidget(self.progress)
        progress_box.setLayout(vbox)
        layout.addWidget(progress_box)

        # --- ボタン群 ---
        btn_box = QtWidgets.QGroupBox("操作")
        btn_box.setStyleSheet(self.groupbox_style())
        btn_layout = QtWidgets.QHBoxLayout()

        self.add_btn = QtWidgets.QPushButton("追加")
        self.edit_btn = QtWidgets.QPushButton("編集")
        self.delete_btn = QtWidgets.QPushButton("削除")
        self.load_btn = QtWidgets.QPushButton("読み込み")
        self.save_btn = QtWidgets.QPushButton("保存")

        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.load_btn, self.save_btn]:
            btn.setStyleSheet(self.button_style())
            btn_layout.addWidget(btn)

        btn_box.setLayout(btn_layout)
        layout.addWidget(btn_box)

        # --- フィルタ ---
        filter_box = QtWidgets.QGroupBox("フィルタ")
        filter_box.setStyleSheet(self.groupbox_style())
        f_layout = QtWidgets.QHBoxLayout()
        f_layout.addWidget(QtWidgets.QLabel("表示:"))
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["全て", "取得済み", "未取得"])
        f_layout.addWidget(self.filter_combo)
        filter_box.setLayout(f_layout)
        layout.addWidget(filter_box)

        self.setLayout(layout)

        # --- ボタンイベント ---
        self.add_btn.clicked.connect(self.add_accessory)
        self.edit_btn.clicked.connect(self.edit_accessory)
        self.delete_btn.clicked.connect(self.delete_accessory)
        self.load_btn.clicked.connect(self.load_csv)
        self.save_btn.clicked.connect(self.save_csv)
        self.filter_combo.currentIndexChanged.connect(self.refresh_table)

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
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #50a0ff;
            }
        """

    # ---------- テーブル操作 ----------
    def refresh_table(self):
        self.table.setRowCount(0)
        filter_text = self.filter_combo.currentText()
        for acc in self.accessories:
            if filter_text != "全て" and acc["obtained"] != filter_text:
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i, key in enumerate(["name","obtained","effect1","effect2","effect3"]):
                item = QtWidgets.QTableWidgetItem(acc[key])
                # ドロップシャドウ
                shadow = QtWidgets.QGraphicsDropShadowEffect()
                shadow.setBlurRadius(3)
                shadow.setOffset(1,1)
                shadow.setColor(QtGui.QColor(128,192,255))
                item.setData(QtCore.Qt.UserRole, shadow)
                self.table.setItem(row,i,item)
        self.update_progress()

    def update_progress(self):
        if not self.accessories:
            self.progress.setValue(0)
            return
        obtained_count = sum(1 for a in self.accessories if a["obtained"]=="取得済み")
        rate = int(obtained_count / len(self.accessories) * 100)
        self.progress.setValue(rate)

    # ---------- アクセサリー操作 ----------
    def add_accessory(self):
        dialog = AccessoryDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.accessories.append(dialog.get_data())
            self.refresh_table()

    def edit_accessory(self):
        row = self.table.currentRow()
        if row < 0:
            return
        filtered = [a for a in self.accessories if self.filter_combo.currentText() in ["全て", a["obtained"]]]
        dialog = AccessoryDialog(self, filtered[row])
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            idx = self.accessories.index(filtered[row])
            self.accessories[idx] = dialog.get_data()
            self.refresh_table()

    def delete_accessory(self):
        row = self.table.currentRow()
        if row < 0:
            return
        filtered = [a for a in self.accessories if self.filter_combo.currentText() in ["全て", a["obtained"]]]
        idx = self.accessories.index(filtered[row])
        del self.accessories[idx]
        self.refresh_table()

    # ---------- CSV ----------
    def save_csv(self):
        path,_ = QtWidgets.QFileDialog.getSaveFileName(self,"CSV保存","","CSVファイル (*.csv)")
        if path:
            with open(path,"w",newline="",encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["名前","取得","効果1","効果2","効果3"])
                for a in self.accessories:
                    writer.writerow([a["name"],a["obtained"],a["effect1"],a["effect2"],a["effect3"]])

    def load_csv(self):
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,"CSV読み込み","","CSVファイル (*.csv)")
        if path:
            with open(path,"r",encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.accessories = []
                for row in reader:
                    # 必ず文字列化して格納
                    self.accessories.append({
                        "name": str(row.get("名前","")),
                        "obtained": str(row.get("取得","未取得")),
                        "effect1": str(row.get("効果1","")),
                        "effect2": str(row.get("効果2","")),
                        "effect3": str(row.get("効果3",""))
                    })
            self.refresh_table()


class AccessoryDialog(QtWidgets.QDialog):
    def __init__(self,parent=None,data=None):
        super().__init__(parent)
        self.setWindowTitle("アクセサリー登録")
        self.setGeometry(500, 250, 400, 220)
        layout = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        self.obtained_combo = QtWidgets.QComboBox()
        self.obtained_combo.addItems(["未取得","取得済み"])
        self.effect1_edit = QtWidgets.QLineEdit()
        self.effect2_edit = QtWidgets.QLineEdit()
        self.effect3_edit = QtWidgets.QLineEdit()
        layout.addRow("名前:",self.name_edit)
        layout.addRow("取得:",self.obtained_combo)
        layout.addRow("効果1:",self.effect1_edit)
        layout.addRow("効果2:",self.effect2_edit)
        layout.addRow("効果3:",self.effect3_edit)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        self.setLayout(layout)

        if data:
            self.name_edit.setText(data["name"])
            self.obtained_combo.setCurrentText(data["obtained"])
            self.effect1_edit.setText(data["effect1"])
            self.effect2_edit.setText(data["effect2"])
            self.effect3_edit.setText(data["effect3"])

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "obtained": self.obtained_combo.currentText(),
            "effect1": self.effect1_edit.text(),
            "effect2": self.effect2_edit.text(),
            "effect3": self.effect3_edit.text()
        }