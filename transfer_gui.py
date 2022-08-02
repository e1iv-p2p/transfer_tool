from PySide2 import QtWidgets, QtCore, QtGui
from . import transfer_defs as td
from . import transfer_arn_rnd_flags as tarf
from . import transfer_hierarchy as th
from . import transfer_maping as tm
from . import transfer_uv as tu
from . import transfer_material as tmat
from . import style_sheets as ss
import pymel.core as pm
from utils import skazka_defs as sk_defs


transfer_win = None

class GuiTransfer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GuiTransfer, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Transfer tool")
        self.setMinimumWidth(500)

        self.selected = pm.ls(sl=True)
        if len(self.selected) != 2:
            pm.warning("how about no? U need to select 2 obj")
            return

        self.dic, self.ns1, self.ns2 = td.get_selected(self.selected)
        if not self.dic:
            return
        self.transfer_map = tm.MapTransfer(self.dic, self.ns1, self.ns2, self)
        self.transfer_hierarhy = th.HierarchyTransfer(self.dic, self.ns1, self.ns2, self)
        self.transfer_uv = tu.TransferUV(self.dic, self.ns1, self.ns2, self)
        self.transfer_flags = tarf.TransferFlags(self.dic, self.ns1, self.ns2, self)
        self.transfer_mat = tmat.TransferMaterials(self.dic, self.ns1, self.ns2, self)
        # self.transfer_mesh = tmesh.TransferMeshes()
        self.create_widgets()
        self.create_layout()
        self.show_no_difference_label()
        self.create_connections()



    def create_widgets(self):
        self.topWidget = QtWidgets.QWidget()
        self.downWidget = QtWidgets.QWidget()

        self.label_no_difference = QtWidgets.QLabel('We have not found difference in the names')
        self.label_no_difference.setHidden(True)

        self.spliter = QtWidgets.QSplitter()
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.transfer_hierarhy, 'Hierarchy')
        self.tab_widget.addTab(self.transfer_uv, 'UVs')
        self.tab_widget.addTab(self.transfer_flags, 'Flags')
        self.tab_widget.addTab(self.transfer_mat, 'Materials')

    def create_layout(self):
        self.main_lo = QtWidgets.QVBoxLayout(self)

        self.tab_lo = QtWidgets.QHBoxLayout(self)
        self.tab_lo.addWidget(self.tab_widget)

        self.name_lo1 = QtWidgets.QHBoxLayout(self)
        self.name_lo1.addWidget(self.transfer_map)
        # self.name_lo1.addWidget(self.map_name)

        self.topWidget.setLayout(self.name_lo1)
        self.downWidget.setLayout(self.tab_lo)


        self.label_lo = QtWidgets.QHBoxLayout(self)
        self.label_lo.addWidget(self.label_no_difference)


        # self.main_lo.addLayout(self.label_lo)
        # self.main_lo.addLayout(self.name_lo1)
        # self.main_lo.addLayout(self.tab_lo)

        self.main_lo.addWidget(self.spliter)

        self.spliter.addWidget(self.topWidget)
        self.spliter.addWidget(self.downWidget)
        self.spliter.setOrientation(QtCore.Qt.Vertical)

    def create_connections(self):
        pass

    def show_no_difference_label(self):
        if not self.dic['dst_only']:
            self.label_no_difference.setHidden(False)
            self.transfer_map.setHidden(True)

    def add_hierarchy_tab(self, dic, ns1, ns2):
        pass

    def update(self):
        self.dic, self.ns1, self.ns2 = td.get_selected()
        self.tab_lo.update()

def create_ui():
    global transfer_win
    q_maya_window = sk_defs.get_maya_window()
    transfer_win = GuiTransfer(parent=q_maya_window)
    transfer_win.show()
    return transfer_win



