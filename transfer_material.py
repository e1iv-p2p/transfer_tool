import collections

from PySide2 import QtWidgets

from . import style_sheets as ss
from . import transfer_defs as td
from . import ui_widgets as uw


class TransferMaterials(QtWidgets.QWidget):
    def __init__(self, dic, ns1, ns2, gui):
        super(TransferMaterials, self).__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.dic, self.ns1, self.ns2, self.gui = dic, ns1, ns2, gui
        self.dic_dif_mat = collections.OrderedDict()
        self.dic_receiver(self.dic)
        self.populate_tree()

    def create_widgets(self):
        self.spliter = QtWidgets.QSplitter()
        self.src_tree = QtWidgets.QTreeWidget()
        self.src_tree.setColumnCount(1)
        self.src_tree.setHeaderLabel('From')

        self.dst_tree = QtWidgets.QTreeWidget()
        self.dst_tree.setColumnCount(3)
        self.dst_tree.setHeaderLabels(['To', '2', 'From'])
        self.dst_tree.setColumnWidth(0, 250)
        self.dst_tree.setColumnHidden(1, True)

        self.transfer_material_btn = uw.Button('Transfer materials')
        self.transfer_material_btn.setStyleSheet(ss.button_ss)

    def create_layout(self):
        self.main_lo = QtWidgets.QHBoxLayout(self)
        self.tree_lo = QtWidgets.QHBoxLayout(self)
        self.button_lo = QtWidgets.QVBoxLayout(self)

        self.main_lo.addLayout(self.tree_lo)
        self.main_lo.addLayout(self.button_lo)

        self.tree_lo.addWidget(self.spliter)
        self.spliter.addWidget(self.src_tree)
        self.spliter.addWidget(self.dst_tree)

        self.button_lo.addWidget(self.transfer_material_btn)

    def create_connections(self):
        self.transfer_material_btn.button_press(self.transfer_material_btn_press)

    def transfer_material_btn_press(self):
        if self.dic_dif_mat:
            for k, shape in self.dic_dif_mat.items():
                print(shape[0], shape[1])
                td.transfer_materials2(shape[0], shape[1], self.dic)
            self.dic_receiver(self.dic)

    def dic_receiver(self, dic):
        flag = 'mat'
        self.dic = dic
        self.dic_dif_mat = td.init_difference_check(self.dic, flag)
        self.populate_tree()

    def populate_tree(self):
        self.dst_tree.clear()
        self.src_tree.clear()
        if self.dic_dif_mat:
            td.populate_tree_with_difference(self.dic_dif_mat, self.src_tree, self.dst_tree)
