# crystal_tool.py
# -*- coding: utf-8 -*-

import sys
import math
from PyQt5 import QtWidgets, QtGui, QtCore


class CrystalTool(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DQ10職人ツール（結晶金策）")
        self.setGeometry(200,100,600,420)

        # 背景色（鍛冶ツールと同じ）
        self.setStyleSheet(
            "background-color:#d0f0fd; font-family:'ＭＳ Ｐゴシック'; font-size:11pt;"
        )

        self.initUI()

    def initUI(self):

        main_layout = QtWidgets.QVBoxLayout(self)

        tabs = QtWidgets.QTabWidget()

        tabs.addTab(self.create_tabA(),"装備・錬金から")
        tabs.addTab(self.create_tabB(),"錬金付き購入")

        main_layout.addWidget(tabs)

        # クリアボタン
        self.clear_btn = QtWidgets.QPushButton("クリア")
        self.clear_btn.setStyleSheet("color:red; font-weight:bold; font-size:12pt;")
        self.clear_btn.clicked.connect(self.clear_all)

        main_layout.addWidget(self.clear_btn)

    # -------------------------
    # タブA（装備＋錬金）
    # -------------------------

    def create_tabA(self):

        box = QtWidgets.QGroupBox("装備・錬金から結晶化")
        box.setStyleSheet(self.groupbox_style())

        layout = QtWidgets.QGridLayout()

        self.equip_price = QtWidgets.QLineEdit("0")
        self.alchemy_price = QtWidgets.QLineEdit("0")
        self.crystal_price = QtWidgets.QLineEdit("0")
        self.crystal_count = QtWidgets.QLineEdit("0")

        self.resultA = QtWidgets.QLabel("0")
        self.resultA.setAlignment(QtCore.Qt.AlignRight)

        # 影（鍛冶ツールと同じ）
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(1,1)
        shadow.setColor(QtGui.QColor(128,192,255))
        self.resultA.setGraphicsEffect(shadow)

        for w in [self.equip_price,self.alchemy_price,self.crystal_price,self.crystal_count]:
            w.textChanged.connect(self.calcA)

        layout.addWidget(QtWidgets.QLabel("装備代"),0,0)
        layout.addWidget(self.equip_price,0,1)

        layout.addWidget(QtWidgets.QLabel("錬金代"),1,0)
        layout.addWidget(self.alchemy_price,1,1)

        layout.addWidget(QtWidgets.QLabel("結晶価格"),2,0)
        layout.addWidget(self.crystal_price,2,1)

        layout.addWidget(QtWidgets.QLabel("結晶個数"),3,0)
        layout.addWidget(self.crystal_count,3,1)

        layout.addWidget(QtWidgets.QLabel("粗利"),4,0)
        layout.addWidget(self.resultA,4,1)

        box.setLayout(layout)

        return box

    def calcA(self):

        try:
            equip = float(self.equip_price.text())
            alchemy = float(self.alchemy_price.text())
            price = float(self.crystal_price.text())
            count = float(self.crystal_count.text())
        except:
            equip=alchemy=price=count=0

        profit = math.ceil(price*count - (equip+alchemy))

        self.resultA.setText(str(profit))

    # -------------------------
    # タブB（購入）
    # -------------------------

    def create_tabB(self):

        box = QtWidgets.QGroupBox("錬金付き装備購入")
        box.setStyleSheet(self.groupbox_style())

        layout = QtWidgets.QGridLayout()

        self.buy_price = QtWidgets.QLineEdit("0")
        self.crystal_priceB = QtWidgets.QLineEdit("0")
        self.crystal_countB = QtWidgets.QLineEdit("0")

        self.resultB = QtWidgets.QLabel("0")
        self.resultB.setAlignment(QtCore.Qt.AlignRight)

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(1,1)
        shadow.setColor(QtGui.QColor(128,192,255))
        self.resultB.setGraphicsEffect(shadow)

        for w in [self.buy_price,self.crystal_priceB,self.crystal_countB]:
            w.textChanged.connect(self.calcB)

        layout.addWidget(QtWidgets.QLabel("購入金額"),0,0)
        layout.addWidget(self.buy_price,0,1)

        layout.addWidget(QtWidgets.QLabel("結晶価格"),1,0)
        layout.addWidget(self.crystal_priceB,1,1)

        layout.addWidget(QtWidgets.QLabel("結晶個数"),2,0)
        layout.addWidget(self.crystal_countB,2,1)

        layout.addWidget(QtWidgets.QLabel("粗利"),3,0)
        layout.addWidget(self.resultB,3,1)

        box.setLayout(layout)

        return box

    def calcB(self):

        try:
            buy = float(self.buy_price.text())
            price = float(self.crystal_priceB.text())
            count = float(self.crystal_countB.text())
        except:
            buy=price=count=0

        profit = math.ceil(price*count - buy)

        self.resultB.setText(str(profit))

    # -------------------------
    # 共通
    # -------------------------

    def clear_all(self):

        for w in [
            self.equip_price,
            self.alchemy_price,
            self.crystal_price,
            self.crystal_count,
            self.buy_price,
            self.crystal_priceB,
            self.crystal_countB
        ]:
            w.setText("0")

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


if __name__=="__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = CrystalTool()
    window.show()

    sys.exit(app.exec_())