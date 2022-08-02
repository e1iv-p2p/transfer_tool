import copy

import pymel.core as pm
from PySide2 import QtWidgets, QtCore

from . import style_sheets as ss
from . import transfer_gui as tg
from . import ui_widgets as uw


class NameTransfer(QtWidgets.QWidget):
    def __init__(self, dic, ns1, ns2):
        super(NameTransfer, self).__init__()
        self.create_widgets()

        self.create_layout()
        self.create_connections()
        self.dic, self.ns1, self.ns2 = dic, ns1, ns2
        self.lst = []
        # self.add_mesh_from()
        self.add_mesh()

    def create_widgets(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.hideColumn(0)
        header_from = QtWidgets.QTableWidgetItem()
        header_from.setText('From')
        self.table.setHorizontalHeaderItem(1, header_from)
        header_to = QtWidgets.QTableWidgetItem()
        header_to.setText('To')
        self.table.setHorizontalHeaderItem(2, header_to)
        self.table.setColumnWidth(1, 290)
        self.table.setColumnWidth(2, 285)

        self.transfer_btn = uw.Button(u"Rename")
        self.transfer_btn.setStyleSheet(ss.button_ss)

        self.addstr_btn = uw.Button(u'Add')
        self.addstr_btn.setStyleSheet(ss.button_ss)


    def create_layout(self):
        self.main_lo = QtWidgets.QVBoxLayout(self)
        self.label_lo = QtWidgets.QHBoxLayout(self)
        self.list_lo = QtWidgets.QHBoxLayout(self)
        self.button_lo = QtWidgets.QHBoxLayout(self)

        self.main_lo.addLayout(self.label_lo)
        self.main_lo.addLayout(self.list_lo)
        self.main_lo.addLayout(self.button_lo)

        self.list_lo.addWidget(self.table)

        self.button_lo.addWidget(self.transfer_btn, alignment=QtCore.Qt.AlignCenter)
        self.button_lo.addWidget(self.addstr_btn, alignment=QtCore.Qt.AlignCenter)

    def create_connections(self):
        self.transfer_btn.button_press(self.rename_mesh)
        self.addstr_btn.button_press(self.add_new)

    def add_mesh(self):
        # Populate table, creating combobox
        if not self.dic['dst_only']:
            pm.warning('We have not found difference in the names')
            return
        self.table.clear()
        self.table.setRowCount(len(self.dic['src_only']))
        i = 0
        for k, v in self.dic['src_only'].items():
            item_path = QtWidgets.QTableWidgetItem(v.longName())
            self.table.setItem(i, 0, item_path)
            item_name = QtWidgets.QTableWidgetItem(k.split('|')[-1])
            self.table.setItem(i, 1, item_name)
            combox = MyCheckBox(index=i, parent=self)
            combox.addItem("<None>", "<None>")
            for k2, v2 in self.dic['dst_only'].items():
                combox.addItem(k2, v2.longName())
                self.table.setCellWidget(i, 2, combox)
            i += 1

    def rename_mesh(self):
        # Rename mapped meshs, change dictionary
        for i in range(self.table.rowCount()):
            combox = self.table.cellWidget(i, 2)
            if combox.currentText() == '<None>':
                continue
            else:
                self.dic['dst_only'].pop(combox.currentText())
                self.dic['src_only'].pop(self.table.item(i, 1).text())
            print('Rename complete.')
            pm.rename(combox.currentData(), self.ns2 + self.table.item(i, 1).text())

            self.dic["both"][combox.currentText()] = [self.ns1 + self.table.item(i, 1).text(), self.ns2 + self.table.item(i, 1).text()]
        print(self.dic)
        self.refresh_ui()

    def refresh_ui(self):
        tg.transfer_win.destroy()
        tg.create_ui()

    def add_new(self):
        combox = MyCheckBox()




class MyCheckBox(QtWidgets.QComboBox):
    def __init__(self, index, parent=None):
        super(MyCheckBox, self).__init__(parent)
        self.parent = parent
        self.index = index
        self.parent.lst.append(self)
        self.cur_data = ""
        self.cur_text = ""
        self.activated.connect(self.current_id_change)

    def current_id_change(self):
        # Combobox logic on value press
        dik = copy.deepcopy(self.parent.dic['dst_only'])
        for i in range(self.parent.table.rowCount()):
            combox = self.parent.table.cellWidget(i, 2)
            current_text = combox.currentText()
            current_data = combox.currentData()
            if current_text != '<None>':
                dik.pop(current_text)
            combox.clear()
            combox.addItem(current_text, current_data)
            if combox.currentText() != '<None>':
                combox.addItem("<None>", "<None>")
        for i in range(self.parent.table.rowCount()):
            combox = self.parent.table.cellWidget(i, 2)
            for k, v in dik.items():
                combox.addItem(k, v.longName())







