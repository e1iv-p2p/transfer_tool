from PySide2 import QtWidgets, QtCore, QtGui

from . import style_sheets as ss
from . import transfer_defs as td
from . import ui_widgets as uw


class HierarchyTransfer(QtWidgets.QWidget):
    def __init__(self, dic, ns1, ns2, gui):
        super(HierarchyTransfer, self).__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.count = 0
        self.dic, self.ns1, self.ns2, self.gui = dic, ns1, ns2, gui
        self.populate_tree()
        self.mapped_item_list = []



    def create_widgets(self):
        self.spliter = QtWidgets.QSplitter()
        self.src_tree = QtWidgets.QTreeWidget()
        self.src_tree.setColumnCount(3)
        self.src_tree.setHeaderLabel('From')
        self.src_tree.setColumnHidden(1, True)
        self.src_tree.setColumnHidden(2, True)
        self.dst_tree = QtWidgets.QTreeWidget()
        self.dst_tree.setColumnCount(3)
        self.dst_tree.setHeaderLabels(['To', '2', 'From'])
        self.dst_tree.setColumnWidth(0, 250)
        self.dst_tree.setColumnHidden(1, True)
        self.btn_difference = uw.Button("Difference")
        self.btn_difference.setStyleSheet(ss.button_ss)
        self.btn_show_all = uw.Button('All')
        self.btn_show_all.setStyleSheet(ss.button_ss)
        self.btn_map = uw.Button('Map')
        self.btn_map.setStyleSheet(ss.button_ss)
        self.btn_transfer_all = uw.Button('Transfer all')
        self.btn_transfer_all.setStyleSheet(ss.button_ss)

    def create_layout(self):
        self.main_lo = QtWidgets.QHBoxLayout(self)
        self.tree_lo = QtWidgets.QHBoxLayout(self)
        self.button_lo = QtWidgets.QVBoxLayout(self)

        self.main_lo.addLayout(self.tree_lo)

        self.tree_lo.addWidget( self.spliter)
        self.spliter.addWidget(self.src_tree)
        self.spliter.addWidget(self.dst_tree)
        self.main_lo.addLayout(self.button_lo)

        self.button_lo.addWidget(self.btn_map)
        self.button_lo.addWidget(self.btn_show_all)
        self.button_lo.addWidget(self.btn_difference)
        self.button_lo.addWidget(self.btn_transfer_all)

    def create_connections(self):

        self.btn_difference.button_press(self.diff_shape_detection)
        self.btn_map.button_press(self.send_maped_node)
        self.btn_show_all.button_press(self.populate_tree)
        self.btn_transfer_all.button_press(self.transfer_all_btn_press)

    def dic_receive(self, dic):
        self.dic = dic
        self.populate_tree()

    def transfer_all_btn_press(self):
        for i in range(self.src_tree.topLevelItemCount()):
            for n in range(self.src_tree.topLevelItem(i).childCount()):
                ggg = self.src_tree.topLevelItem(i).child(n)
                for z in range(ggg.childCount()):
                    www = ggg.child(z)
                    if "Shape" in www.text(0):
                        www.setBackground(0, QtGui.QBrush(QtGui.QColor('#211a24')))

    def populate_tree(self):
        self.dst_tree.clear()
        self.src_tree.clear()
        td.populate_tree(self.dic, self.src_tree, self.dst_tree)

    def clean_mapped_list_after_rename(self):
        self.mapped_item_list = []

    def send_maped_node(self):
        item_from = self.src_tree.currentItem()
        item_to = self.dst_tree.currentItem()
        print(item_from.text(0), item_to.text(0))
        if not item_from.text(0) or not item_to.text(0):
            return
        if item_from.text(0) == item_to.text(0):
            return
        if 'Shape' in item_from.text(0) and 'Shape' in item_to.text(0):
            # if 'Shape' in item_from.text(0) and 'Shape' in item_to.text(0):
            self.mapped_item_list.append(td.add_maped_node_to_dic(item_from.text(0), item_to.text(0), str(item_to), item_to, self.dic, self.mapped_item_list))
            self.dic = td.dic_map_populate(self.dic, self.mapped_item_list)

            self.gui.transfer_map.dic_receiver(self.dic, self.mapped_item_list)
            item_to.setText(2, item_from.text(0))


    def diff_shape_detection(self):
        self.dst_tree.clear()
        self.src_tree.clear()
        td.diff_shape_detection(self.dic, self.src_tree, self.dst_tree)
