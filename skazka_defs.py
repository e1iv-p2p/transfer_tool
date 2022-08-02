import os
import re
import json
import sys
import traceback
import subprocess
from functools import wraps
import mmap
import collections

try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    import maya.OpenMayaUI as omui
    import maya.mel as mel
    import pymel.core as pm
    from utils.Qt import QtWidgets, QtCore, QtGui

    from shiboken2 import wrapInstance as wrp
    from shiboken2 import getCppPointer as cpp

    _DPI_SCALE = 1.0 if not hasattr(cmds, "mayaDpiSetting") else cmds.mayaDpiSetting(query=True, realScaleValue=True)
except ImportError:
    pass
except AttributeError:
    pass

try:    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    long
except NameError:   # Python 3 compatibility
    long = int
    unicode = str

def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrp(long(ptr), QtWidgets.QMainWindow)