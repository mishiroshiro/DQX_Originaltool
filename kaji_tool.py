# kaji_tool.py
# -*- coding: utf-8 -*-
import sys, os, json, math, time
from PyQt5 import QtWidgets, QtGui, QtCore

class KajiTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DQ10職人ツール（鍛冶）")
        self.setGeometry(200, 100, 800, 780)
        self.setStyleSheet("background-color:#d0f0fd; font-family:'ＭＳ Ｐゴシック'; font-size:11pt;")

        # データ初期化
        self.materials = []
        self.sell_prices = {"☆0":0, "☆1":0, "☆2":0, "☆3":0}
        self.counts = {"失敗":0, "成功0":0, "成功1":0, "成功2":0, "大成功3":0}
        self.hammer_price = 0
        self.hammer_max = 60
        self.production_count = 1
        self.save_folder = None

        # GUI作成
        self.initUI()
        self.update_display()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # --- 制作回数 ---
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("今回の制作回数"))
        self.prod_combo = QtWidgets.QComboBox()
        self.prod_combo.addItems([str(i) for i in range(1, 31)])
        self.prod_combo.setCurrentIndex(0)
        self.prod_combo.currentIndexChanged.connect(self.change_production_count)
        hbox.addWidget(self.prod_combo)
        layout.addLayout(hbox)

        # --- ハンマー情報 ---
        hammer_box = QtWidgets.QGroupBox("ハンマー情報")
        hammer_box.setStyleSheet(self.groupbox_style())
        hb = QtWidgets.QGridLayout()
        hb.addWidget(QtWidgets.QLabel("購入価格"), 0, 0)
        self.hammer_price_input = QtWidgets.QLineEdit("0")
        hb.addWidget(self.hammer_price_input, 0, 1)
        hb.addWidget(QtWidgets.QLabel("最大使用回数"), 1, 0)
        self.hammer_max_input = QtWidgets.QLineEdit("60")
        hb.addWidget(self.hammer_max_input, 1, 1)
        hb.addWidget(QtWidgets.QLabel("1制作あたり費用"), 2, 0)
        self.hammer_unit_label = QtWidgets.QLabel("0")
        hb.addWidget(self.hammer_unit_label, 2, 1)
        hammer_box.setLayout(hb)
        layout.addWidget(hammer_box)

        # --- 素材情報 ---
        self.mat_box = QtWidgets.QGroupBox("素材情報")
        self.mat_box.setStyleSheet(self.groupbox_style())
        self.mat_layout = QtWidgets.QGridLayout()
        self.mat_layout.addWidget(QtWidgets.QLabel("素材名"), 0, 0)
        self.mat_layout.addWidget(QtWidgets.QLabel("単価"), 0, 1)
        self.mat_layout.addWidget(QtWidgets.QLabel("必要数"), 0, 2)
        self.mat_layout.addWidget(QtWidgets.QLabel("1つ当たり原価"), 0, 3)
        add_mat_btn = QtWidgets.QPushButton("素材追加")
        add_mat_btn.clicked.connect(self.add_material)
        add_mat_btn.setStyleSheet(self.button_style())
        self.mat_layout.addWidget(add_mat_btn, 0, 4)
        self.mat_box.setLayout(self.mat_layout)
        layout.addWidget(self.mat_box)

        # --- 販売価格 ---
        sell_box = QtWidgets.QGroupBox("今回制作アイテム販売価格")
        sell_box.setStyleSheet(self.groupbox_style())
        sell_layout = QtWidgets.QGridLayout()
        self.sell_inputs = {}
        for i, star in enumerate(["☆0","☆1","☆2","☆3"]):
            sell_layout.addWidget(QtWidgets.QLabel(star), i, 0)
            inp = QtWidgets.QLineEdit("0")
            inp.setAlignment(QtCore.Qt.AlignRight)
            sell_layout.addWidget(inp, i, 1)
            self.sell_inputs[star] = inp
        sell_box.setLayout(sell_layout)
        layout.addWidget(sell_box)

        # --- 成功率カウント ---
        count_box = QtWidgets.QGroupBox("成功率カウント")
        count_box.setStyleSheet(self.groupbox_style())
        self.count_labels = {}
        count_layout = QtWidgets.QGridLayout()
        for i, (k, v) in enumerate(self.counts.items()):
            count_layout.addWidget(QtWidgets.QLabel(k), i, 0)
            plus_btn = QtWidgets.QPushButton("+")
            plus_btn.clicked.connect(lambda _, key=k: self.increment_count(key))
            plus_btn.setStyleSheet(self.button_style())
            count_layout.addWidget(plus_btn, i, 1)
            minus_btn = QtWidgets.QPushButton("-")
            minus_btn.clicked.connect(lambda _, key=k: self.decrement_count(key))
            minus_btn.setStyleSheet(self.button_style())
            count_layout.addWidget(minus_btn, i, 2)
            lbl = QtWidgets.QLabel("0")
            lbl.setAlignment(QtCore.Qt.AlignRight)
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(3)
            shadow.setOffset(1,1)
            shadow.setColor(QtGui.QColor(128,192,255))
            lbl.setGraphicsEffect(shadow)
            count_layout.addWidget(lbl, i, 3)
            self.count_labels[k] = lbl
        count_box.setLayout(count_layout)
        layout.addWidget(count_box)

        # --- 統計 ---
        stat_box = QtWidgets.QGroupBox("統計")
        stat_box.setStyleSheet(self.groupbox_style())
        stat_layout = QtWidgets.QGridLayout()
        self.total_cost_label = QtWidgets.QLabel("0")
        self.total_sell_label = QtWidgets.QLabel("0")
        self.profit_label = QtWidgets.QLabel("0")
        self.success_rate_label = QtWidgets.QLabel("0")
        self.breakeven_label = QtWidgets.QLabel("0")
        for lbl in [self.total_cost_label,self.total_sell_label,self.profit_label,self.success_rate_label,self.breakeven_label]:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(3)
            shadow.setOffset(1,1)
            shadow.setColor(QtGui.QColor(128,192,255))
            lbl.setGraphicsEffect(shadow)
        stat_layout.addWidget(QtWidgets.QLabel("総原価"),0,0); stat_layout.addWidget(self.total_cost_label,0,1)
        stat_layout.addWidget(QtWidgets.QLabel("総売価"),1,0); stat_layout.addWidget(self.total_sell_label,1,1)
        stat_layout.addWidget(QtWidgets.QLabel("利益"),2,0); stat_layout.addWidget(self.profit_label,2,1)
        stat_layout.addWidget(QtWidgets.QLabel("大成功率(%)"),3,0); stat_layout.addWidget(self.success_rate_label,3,1)
        stat_layout.addWidget(QtWidgets.QLabel("損益分岐点(%)"),4,0); stat_layout.addWidget(self.breakeven_label,4,1)
        stat_box.setLayout(stat_layout)
        layout.addWidget(stat_box)

        # --- 保存・読み込み ---
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_folder_btn = QtWidgets.QPushButton("保存フォルダ選択")
        self.save_folder_btn.clicked.connect(self.select_save_folder)
        self.save_folder_btn.setStyleSheet(self.button_style())
        btn_layout.addWidget(self.save_folder_btn)
        self.save_btn = QtWidgets.QPushButton("入力内容保存")
        self.save_btn.clicked.connect(self.save_input)
        self.save_btn.setStyleSheet(self.button_style())
        btn_layout.addWidget(self.save_btn)
        self.load_btn = QtWidgets.QPushButton("JSON読み込み")
        self.load_btn.clicked.connect(self.load_input_file)
        self.load_btn.setStyleSheet(self.button_style())
        btn_layout.addWidget(self.load_btn)
        layout.addLayout(btn_layout)

        # --- クリアボタン ---
        self.clear_btn = QtWidgets.QPushButton("すべてクリア")
        self.clear_btn.setStyleSheet("color:red; font-weight:bold; font-size:12pt;")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)

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
            QPushButton:pressed {
                background-color: #50a0ff;
            }
        """

    # ---------- 機能 ----------
    def change_production_count(self, index):
        self.production_count = int(self.prod_combo.currentText())
        self.update_display()

    def add_material(self):
        row = len(self.materials)+1
        name_input = QtWidgets.QLineEdit("")
        price_input = QtWidgets.QLineEdit("0")
        qty_input = QtWidgets.QLineEdit("1")
        subtotal_label = QtWidgets.QLabel("0")
        subtotal_label.setAlignment(QtCore.Qt.AlignRight)
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(1,1)
        shadow.setColor(QtGui.QColor(128,192,255))
        subtotal_label.setGraphicsEffect(shadow)
        self.mat_layout.addWidget(name_input,row,0)
        self.mat_layout.addWidget(price_input,row,1)
        self.mat_layout.addWidget(qty_input,row,2)
        self.mat_layout.addWidget(subtotal_label,row,3)
        self.materials.append((name_input,price_input,qty_input,subtotal_label))
        name_input.textChanged.connect(self.update_display)
        price_input.textChanged.connect(self.update_display)
        qty_input.textChanged.connect(self.update_display)
        self.update_display()

    def update_display(self):
        # ハンマー単価
        try:
            self.hammer_price = float(self.hammer_price_input.text())
            self.hammer_max = int(self.hammer_max_input.text())
            unit_cost = math.ceil(self.hammer_price/self.hammer_max) if self.hammer_max>0 else 0
            self.hammer_unit_label.setText(str(unit_cost))
        except:
            unit_cost = 0
            self.hammer_unit_label.setText("0")

        # 素材合計
        total_material = 0
        for name, price, qty, label in self.materials:
            try:
                p = int(price.text())
                q = int(qty.text())
                subtotal = math.ceil(p*q)
            except:
                subtotal = 0
            label.setText(str(subtotal))
            total_material += subtotal

        per_item_cost = total_material + unit_cost
        total_cost = self.production_count * per_item_cost
        self.total_cost_label.setText(str(total_cost))

        total_sell = 0
        for star in ["☆0","☆1","☆2","☆3"]:
            try:
                val = int(self.sell_inputs[star].text())
            except:
                val = 0
            self.sell_prices[star] = val
            key_map = {"☆0":"成功0","☆1":"成功1","☆2":"成功2","☆3":"大成功3"}
            total_sell += self.counts[key_map[star]]*val
        self.total_sell_label.setText(str(total_sell))

        profit = math.ceil(total_sell - total_cost - (total_sell*0.05) - 5)
        self.profit_label.setText(str(profit))

        total_attempt = sum(self.counts.values())
        success_rate = self.counts["大成功3"]/total_attempt*100 if total_attempt>0 else 0
        self.success_rate_label.setText(str(round(success_rate,1)))

        breakeven = math.ceil(total_cost/total_sell*100) if total_sell>0 else 0
        self.breakeven_label.setText(str(breakeven))

        for k in self.counts:
            self.count_labels[k].setText(str(self.counts[k]))

    def increment_count(self,key):
        self.counts[key] += 1
        self.update_display()
    def decrement_count(self,key):
        if self.counts[key] > 0:
            self.counts[key] -= 1
        self.update_display()

    def clear_all(self):
        self.counts = {k:0 for k in self.counts}
        self.hammer_price_input.setText("0")
        self.hammer_max_input.setText("60")
        self.production_count = 1
        self.prod_combo.setCurrentIndex(0)
        for star in ["☆0","☆1","☆2","☆3"]:
            self.sell_inputs[star].setText("0")
        for name,price,qty,label in self.materials:
            name.setText(""); price.setText("0"); qty.setText("1")
        self.update_display()

    def select_save_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self,"保存フォルダ選択")
        if folder:
            self.save_folder = folder

    def save_input(self):
        if not self.save_folder or not os.path.exists(self.save_folder):
            QtWidgets.QMessageBox.warning(self,"エラー","保存先を選択してください")
            return
        data = {"materials":[],"hammer":{"price":self.hammer_price,"max":self.hammer_max},
                "sell_prices":self.sell_prices,"counts":self.counts,"production_count":self.production_count}
        for name,price,qty,label in self.materials:
            data["materials"].append([name.text(),price.text(),qty.text()])
        fname = f"dq10_input_{int(time.time())}.json"
        with open(os.path.join(self.save_folder,fname),"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
        QtWidgets.QMessageBox.information(self,"保存完了",f"{fname} を保存しました")

    def load_input_file(self):
        file_path,_ = QtWidgets.QFileDialog.getOpenFileName(self,"JSONファイル読み込み","","JSON Files (*.json)")
        if not file_path: return
        with open(file_path,"r",encoding="utf-8") as f:
            data = json.load(f)
        self.hammer_price_input.setText(str(data["hammer"]["price"]))
        self.hammer_max_input.setText(str(data["hammer"]["max"]))
        self.production_count = data.get("production_count",1)
        self.prod_combo.setCurrentIndex(self.production_count-1)
        for star in ["☆0","☆1","☆2","☆3"]:
            self.sell_inputs[star].setText(str(data["sell_prices"].get(star,0)))
        self.counts = data.get("counts",self.counts)
        for name,price,qty in data.get("materials",[]):
            self.add_material()
            self.materials[-1][0].setText(name)
            self.materials[-1][1].setText(str(price))
            self.materials[-1][2].setText(str(qty))
        self.update_display()


if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = KajiTool()
    window.show()
    sys.exit(app.exec_())