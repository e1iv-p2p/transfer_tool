from PySide2 import QtWidgets

from . import style_sheets as ss
from . import transfer_defs as td
from . import ui_widgets


class MapTransfer(QtWidgets.QWidget):
    def __init__(self, dic, ns1, ns2, gui):
        super(MapTransfer, self).__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.list = []
        self.count = 0
        self.dic, self.ns1, self.ns2, self.gui = dic, ns1, ns2, gui

    def create_widgets(self):
        self.map_table = QtWidgets.QTableWidget()
        self.map_table.setColumnCount(4)
        self.map_table.setColumnWidth(1, 500)
        self.map_table.setColumnWidth(0, 395)
        self.map_table.setColumnHidden(3, True)
        self.map_table.setMinimumWidth(1000)
        self.map_table.setMaximumHeight(300)
        self.map_table.setMaximumWidth(1001)
        self.header_to_name()

        self.rename_btn = ui_widgets.Button('Rename')
        self.rename_btn.setStyleSheet(ss.button_ss)
        self.rename_btn.setMaximumWidth(110)

    def create_layout(self):
        self.main_lo = QtWidgets.QHBoxLayout(self)

        self.main_lo.addWidget(self.map_table)
        self.main_lo.addWidget(self.rename_btn)

    def create_connections(self):
        self.rename_btn.button_press(self.on_rename_click)

    def dic_receiver(self, dic, list_map):
        self.map_table.clear()
        self.dic, self.list = dic, list_map
        print(self.list)
        if self.list:
            self.map_table.setRowCount(len(list_map))
            for i, di in enumerate(self.list):
                print(i, di)
                td.add_node_to_name_table(di, i, DelButton(index=i, parent=self), self.map_table)
        self.gui.transfer_uv.dic_receiver(self.dic)
        self.gui.transfer_flags.dic_receiver(self.dic)
        self.gui.transfer_mat.dic_receiver(self.dic)


    def on_rename_click(self):
        self.dic = td.on_rename_btn_click(self.dic, self.list)
        self.list = []
        self.count = 0
        self.map_table.clear()
        self.map_table.setRowCount(0)
        self.header_to_name()
        self.gui.transfer_hierarhy.clean_mapped_list_after_rename()
        self.gui.transfer_uv.dic_receiver(self.dic)
        self.gui.transfer_hierarhy.dic_receive(self.dic)
        self.gui.transfer_flags.dic_receiver(self.dic)
        self.gui.transfer_mat.dic_receiver(self.dic)
        self.gui.transfer_hierarhy.populate_tree()

    def header_to_name(self):
        header_from = QtWidgets.QTableWidgetItem()
        header_from.setText('From')
        self.map_table.setHorizontalHeaderItem(0, header_from)
        header_to = QtWidgets.QTableWidgetItem()
        header_to.setText('To')
        self.map_table.setHorizontalHeaderItem(1, header_to)
        header_button = QtWidgets.QTableWidgetItem()
        header_button.setText('')
        self.map_table.setHorizontalHeaderItem(2, header_button)

    def dictionary_change(self, map_key, index):
        self.dic['map'].popitem(map_key)
        row_dic = self.list.pop(index)
        item = row_dic['obj']
        item.setText(2, '')
        self.dic_receiver(self.dic, self.list)
        # td.add_node_to_name_table(self.dic, self.map_table, self.list, self.count,
        #                           DelButton(index=self.count, parent=self))


class DelButton(QtWidgets.QPushButton):
    def __init__(self, index, parent=None):
        super(DelButton, self).__init__()
        self.table = parent
        self.index = index
        self.setText('Delete')
        self.clicked.connect(self.delete_row)

    def delete_row(self):
        # to_tree_item = self.table.map_table.item(self.index, 3).data(0)

        src_key = self.table.map_table.item(self.index, 0).text().split(':')[-1]

        self.table.map_table.removeRow(self.index)
        self.table.dictionary_change(src_key, self.index)
