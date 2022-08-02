import collections
import maya.cmds as mc
import pymel.core as pm
from PySide2 import QtCore, QtGui
from PySide2 import QtWidgets

selected = pm.ls(sl=True)
ns1 = selected[0].namespace()
ns2 = selected[1].namespace()
render_stats_list = ['castsShadows', 'receiveShadows', 'holdOut', 'motionBlur', 'primaryVisibility', 'smoothShading',
                     'visibleInReflections', 'visibleInRefractions', 'doubleSided', 'geometryAntialiasingOverride',
                     'shadingSamplesOverride']

'''
At the beginning was... self. dic, ns1, ns2
'''


def get_selected(selected, node_type=None, progbar=None):
    '''

    :param selected: Selected outliner root
    :param node_type: List of node types
    :param progbar: QtWidgets.QProgressBar()
    :return:
    '''
    sn1 = selected[0].namespace()
    sn2 = selected[1].namespace()
    print(type(node_type))
    dic = {'both': collections.OrderedDict(), 'src_only': collections.OrderedDict(),
           'dst_only': collections.OrderedDict(), 'map': collections.OrderedDict()}
    lst_from = list()
    lst_to = list()
    # dic = {'both': {str_name: [nt.mesh(), nt.mesh(), ...]}, 'src_only': {}, 'dst_only': {}}

    if not node_type:
        lst_from = pm.listRelatives(selected[0], ad=True, type="mesh", ni=True)
        lst_to = pm.listRelatives(selected[1], ad=True, type="mesh", ni=True)
    elif node_type == 'all':
        lst_from = pm.listRelatives(selected[0], ad=True, ni=True)
        lst_to = pm.listRelatives(selected[1], ad=True, ni=True)
    else:
        for n in node_type:
            src = pm.listRelatives(selected[0], ad=True, type="{}".format(n), ni=True)
            dst = pm.listRelatives(selected[1], ad=True, type="{}".format(n), ni=True)
            lst_from.extend(src)
            lst_to.extend(dst)
    lst_to2 = lst_to[:]

    if progbar:
        progbar.setVisible(True)
        progbar.setMaximum(len(lst_from))
    for n, s1 in enumerate(lst_from):
        if progbar:
            progbar.setValue(n)

        a = s1.name(stripNamespace=True).split("|")[-1]
        found = False
        for s2 in lst_to:
            b = s2.name(stripNamespace=True).split("|")[-1]
            if a == b:
                dic['both'][a] = [s1, s2]
                lst_to2.remove(s2)
                found = True
                break
        if not found:
            node_type = pm.PyNode(s1).nodeType()
            dic['src_only'][a] = s1, {'type': node_type}
    for x in lst_to2:
        node_type = pm.PyNode(x).nodeType()
        b = x.name(stripNamespace=True)
        dic['dst_only'][b] = x, {'type': node_type}

    if progbar:
        progbar.setVisible(False)

    # print dic['both']
    # print dic['src_only']
    # print dic['dst_only']
    return dic, sn1, sn2

'''Mapping defs'''


def add_node_to_name_table(dic, count, btn, map_table):

    item1 = QtWidgets.QTableWidgetItem(dic['key_src'])
    item2 = QtWidgets.QTableWidgetItem(dic['key_dst'])
    item_dst = QtWidgets.QTableWidgetItem(dic['obj_dst'])
    item_dst.setData(QtCore.Qt.UserRole, dic['obj'])
    del_btn = btn

    map_table.setItem(count, 0, item1)
    map_table.setItem(count, 1, item2)
    map_table.setCellWidget(count, 2, del_btn)
    map_table.setItem(count, 3, item_dst)



def dic_map_populate(dic, list_map):
    print('list_map', list_map)
    for x in list_map:
        if x['key_src'].split(':')[-1] in dic['src_only'].keys():
            if x['key_dst'].split(':')[-1] in dic['dst_only'].keys():
                dic['map'][x['key_src'].split(':')[-1]] = [dic['src_only'][x['key_src'].split(':')[-1]], dic['dst_only'][x['key_dst'].split(':')[-1]]]
    return dic
def on_rename_btn_click(dic, list):
    if not list:
        return
    for x in list:
        if x['key_src'] in dic['src_only'].keys():
            if x['key_dst'] in dic['dst_only'].keys():
                dst_both = dic['dst_only'].pop(x['key_dst'])
                src_both = dic['src_only'].pop(x['key_src'])
                dic['both'][x['key_src']] = [pm.PyNode(src_both)]
                dst_both = pm.rename(dst_both, x['key_src'])
                dic['both'][x['key_src']].append(pm.PyNode(dst_both))
    print(dic['both'])
    print(dic['map'])
    dic['map'] = {}
    return dic


'''Difference detection machine'''


def init_difference_check(dic, flag):
    dic_dif = {}

    for k, v in dic.get('both', {}).items():
        if flag == 'uv':
            dic_dif = uv_difference_detection(v[0], v[1], dic_dif)
        if flag == 'render':
            dic_dif = arnold_flags_difference_detection(v[0], v[1], dic_dif)
        if flag == 'mat':
            dic_dif = mat_difference_detection(v[0], v[1], dic_dif)
        if flag == 'mesh':
            dic_dif = mesh_difference_detection(v[0], v[1], dic_dif)

    for k, v in dic.get('map', {}).items():
        if flag == 'uv':
            dic_dif = uv_difference_detection(v[0], v[1], dic_dif)
        if flag == 'render':
            dic_dif = arnold_flags_difference_detection(v[0], v[1], dic_dif)
        if flag == 'mat':
            dic_dif = mat_difference_detection(v[0], v[1], dic_dif)
        if flag == 'mesh':
            dic_dif = mesh_difference_detection(v[0], v[1], dic_dif)
    return dic_dif


'''Mesh transfer defs'''


def mesh_difference_detection(src_shape, dst_shape, dic_dif_mesh=None):
    pass


'''Materials transfer defs'''


def mat_difference_detection(shape_src, shape_dst, dic_dif_mat=None):
    key = shape_src.name(stripNamespace=True).split("|")[-1]
    node_src = pm.PyNode(shape_src)
    node_dst = pm.PyNode(shape_dst)
    se_src = node_src.outputs(type="shadingEngine")
    if not se_src:
        pm.warning('{} without shadingEngine!'.format(shape_src))
        return
    se_dst = node_dst.outputs(type="shadingEngine")
    mat_src = se_src[0].surfaceShader.inputs()
    mat_src = mat_src[0]
    mat_src_attr_list = mat_src.listAttr(u=True, v=True, r=True, w=True, s=True)
    if se_dst:
        mat_dst = se_dst[0].surfaceShader.inputs()
        mat_dst = mat_dst[0]
        mat_dst_attr_list = mat_dst.listAttr(u=True, v=True, r=True, w=True, s=True)
        mat_dst_attr_list_unpack = []
        mat_src_attr_list_unpack = []
        for attr_src in mat_src_attr_list:
            mat_src_attr_list_unpack.append(attr_src.get())
        for attr_dst in mat_dst_attr_list:
            mat_dst_attr_list_unpack.append(attr_dst.get())
        if mat_src_attr_list_unpack != mat_dst_attr_list_unpack:
            dic_dif_mat[key] = [shape_src, shape_dst]
    else:
        dic_dif_mat[key] = [shape_src, shape_dst]

    return dic_dif_mat


def transfer_materials2(shape_from, shape_to, dic_main):
    shape_src = pm.PyNode(shape_from)
    shape_dst = pm.PyNode(shape_to)
    se_dst_lst = shape_dst.outputs(type="shadingEngine")
    mat_dst = []
    for se in se_dst_lst:
        mat_dst.append(se.surfaceShader.inputs()[0])
    pm.delete(mat_dst)
    pm.delete(se_dst_lst)
    dic_processed_se = {}
    se_src_lst = set(shape_src.outputs(type="shadingEngine"))
    for se in se_src_lst:
        if se in dic_processed_se:
            continue
        store_conns_for_se(se, dic_processed_se, dic_main)


def store_conns_for_se(se, dic, dic_main):
    shapes_nodes = pm.ls(se.members(flatten=True), flatten=True)
    new_se = se.duplicate(un=1, ic=1)[0]
    for x in shapes_nodes:
        short_node_str = x.node().name().split(":")[-1].split("|")[-1]
        face_arg = x.split('.')[-1]
        if not 'f[' in face_arg:
            flist = mc.polyListComponentConversion(x.node().name(), tf=True)
            for v in flist:
                face_arg = v.split('.')[-1]
        new_shape = None
        if short_node_str in dic_main['both']:
            new_shape = dic_main['both'][short_node_str][1]
        if short_node_str in dic_main['map']:
            new_shape = dic_main['map'][short_node_str][1]
        if new_shape is None:
            continue

        pm.sets(new_se, e=1, forceElement=new_shape + '.' + face_arg)
    # dic[se] = True


'''Arnold flags transfer defs'''


def arnold_flags_difference_detection(shape_src, shape_dst, dic_dif_flags=None):
    ai_attr_list = pm.listAttr(shape_src, st='ai*', u=True, v=True, r=True, w=True, s=True)
    all_attr_list = ai_attr_list + render_stats_list
    key = shape_src.name(stripNamespace=True).split("|")[-1]
    for attr in all_attr_list:
        if pm.getAttr(shape_src + '.' + attr) != pm.getAttr(shape_dst + '.' + attr):
            dic_dif_flags[key] = [shape_src, shape_dst]
    return dic_dif_flags

def all_attr_list_get(shape):
    ai_attr_list = pm.listAttr(shape, st='ai*', u=True, v=True, r=True, w=True, s=True)
    all_attr_list = ai_attr_list + render_stats_list
    return all_attr_list

def transfer_arn_flags(dic):
    if dic:
        for k, shape in dic.items():
            all_attr_list = all_attr_list_get(shape[0])
            for attr in all_attr_list:
                pm.setAttr(shape[1] + '.' + attr, pm.getAttr(shape[0] + '.' + attr))
    pm.warning('Attribute transfer complete!')


'''UV transfer defs'''


def uv_difference_detection(shape_src, shape_dst, dic_dif_uv=None):
    key = shape_src.name(stripNamespace=True).split("|")[-1]
    dic_dif_uv = dic_dif_uv or {}
    if shape_src.numUVs() != shape_dst.numUVs():
        # pm.warning(shape_src + "Not equal" + shape_dst)
        dic_dif_uv[key] = [shape_src, shape_dst]
    else:
        for idx in range(shape_src.numUVs()):
            if shape_src.getUV(idx) != shape_dst.getUV(idx):
                # pm.warning("Not equal")
                dic_dif_uv[key] = [shape_src, shape_dst]
                break
            else:
                break
    return dic_dif_uv


def transfer_uv(dic):
    if dic:
        for k, node in dic.items():

           # print(node[0], node[1])
            parent_transform = pm.listRelatives(node[1], p=True, type='transform')[0]

            obj_list = pm.listRelatives(parent_transform, c=1)
            #print('obj_list', obj_list)

            target = [x for x in obj_list if "Orig" in x.name()]
            if target:
                pm.setAttr(target[0].name() + '.intermediateObject', 0)

                pm.polyTransfer(target[0].name(), uv=1, ao=node[0].name())
                pm.delete(target[0], ch=True)
            else:
                pm.polyTransfer(node[1].name(), uv=1, ao=node[0].name())

        pm.warning('UV transfer complete!')


def save_inputs(in_mesh):
    conns = mc.listConnections(in_mesh, c=True, p=True, s=True, d=False)
    if not conns:
        return []
    i = 0
    temp_list = []
    while i < len(conns) - 1:
        temp_list.append({'from' : conns[i + 1], 'to': conns[i]})
        i += 2
    return temp_list


def restore_inputs(list_conns):
    for x in list_conns:
        try:
            mc.connectAttr(x['from'], x['to'])
        except:
            print("AAAAA")






'''Hierarchy transfer defs'''


def diff_shape_detection(dic, src_tree, dst_tree):

    diff1 = set(dic['src_only'].keys()) - set(dic['dst_only'].keys())

    diff2 = set(dic['dst_only'].keys()) - set(dic['src_only'].keys())

    build_tree_with_diff_shapes(diff1, diff2, src_tree, dst_tree)

def build_tree_with_diff_shapes(diff1, diff2, src_tree, dst_tree):
    dif_src = diff1
    dif_dst = diff2
    for i in dif_src:
        name = ns1 + ':' + i
        node = pm.PyNode(name)
        insert_long_name_to_tree(node[0].longName(), src_tree, selected[0])

    for i in dif_dst:
        name = ns2 + ':' + i
        node = pm.PyNode(name)
        insert_long_name_to_tree(node[0].longName(), dst_tree, selected[1])


def add_maped_node_to_dic(key_src, key_dst, obj_dst, obj, dic, dic_list):
    if key_src.split(':')[-1] not in dic['src_only']:
        return
    if key_dst.split(':')[-1] not in dic['dst_only']:
        return
    for x in dic_list:
        if key_dst.split(':')[-1] in x['key_dst']:
            return
        if key_src.split(':')[-1] in x['key_src']:
            return
    table_dic = {'key_src': key_src.split(':')[-1], 'key_dst': key_dst.split(':')[-1], 'obj_dst': obj_dst, 'obj': obj}
    return table_dic


'''Populate tree defs'''


def populate_tree(dic, src_tree, dst_tree):
    for k, v in dic.get('both', {}).items():
        insert_long_name_to_tree(v[0].longName(), src_tree, selected[0])
        insert_long_name_to_tree(v[1].longName(), dst_tree, selected[1])

    for k, v in dic.get('src_only', {}).items():
        node = v
        insert_long_name_to_tree(node[0].longName(), src_tree, selected[0])

    for k, v in dic.get('dst_only', {}).items():
        node = v
        insert_long_name_to_tree(node[0].longName(), dst_tree, selected[1])


def populate_tree_with_difference(dic, src_tree, dst_tree):
    if dic:
        for v in dic.values():
            insert_long_name_to_tree(v[0].longName(), src_tree, selected[0])
            insert_long_name_to_tree(v[1].longName(), dst_tree, selected[1])




def insert_long_name_to_tree(long_name, tree, selected_root):
    root_ln = selected_root.longName(stripNamespace=True)
    root_sn = selected_root.name(stripNamespace=True).split("|")[-1]
    long_name = long_name.replace(root_ln, "")
    parent_item_name = root_sn
    parent_item = None
    for i in range(tree.topLevelItemCount()):
        if tree.topLevelItem(i).text(0) == parent_item_name:
            parent_item = tree.topLevelItem(i)
            break
    if parent_item is None:
        parent_item = QtWidgets.QTreeWidgetItem([parent_item_name])
        tree.addTopLevelItem(parent_item)
    make_tree(parent_item, long_name.split('|')[1:])


def find_children(item):
    dic = {}
    for i in range(item.childCount()):
        dic[item.child(i).text(0).split(":")[-1]] = item.child(i)
    return dic


def make_tree(prev_item, str_list):
    if not str_list:
        return
    ex_item = find_existing_child(prev_item, str_list[0])
    if ex_item is not None:
        new_item = ex_item
    else:
        new_item = QtWidgets.QTreeWidgetItem([str_list[0], str_list[0].split(":")[-1]])
        prev_item.addChild(new_item)
        prev_item.setExpanded(True)
        if "Shape" in new_item.text(0):
            new_item.setBackground(0, QtGui.QBrush(QtGui.QColor('#333333')))
    make_tree(new_item, str_list[1:])


def recursive_shit(dic_from, dic_to):
    if not dic_from or not dic_to:
        return
    diff1 = set(dic_from.keys()) - set(dic_to.keys())
    diff2 = set(dic_to.keys()) - set(dic_from.keys())
    inter = set(dic_to.keys()).intersection(set(dic_from.keys()))
    for x in diff1:
        dic_from[x].setBackground(0, QtGui.QBrush(QtGui.QColor('#333333')))
    for x in diff2:
        dic_to[x].setBackground(0, QtGui.QBrush(QtGui.QColor('#333333')))
    for x in inter:
        new_item_a = dic_from[x]
        new_item_b = dic_to[x]
        new_dic_a = find_children(new_item_a)
        new_dic_b = find_children(new_item_b)
        recursive_shit(new_dic_a, new_dic_b)


def find_existing_child(item, str_text):
    for i in range(item.childCount()):
        if item.child(i).text(0) == str_text:
            return item.child(i)

    return None

######################### Return All Item In Tree ##########################

def get_subtree_nodes( tree_widget_item):
    """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
    nodes = list()
    nodes.append(tree_widget_item)
    for i in range(tree_widget_item.childCount()):
        nodes.extend(get_subtree_nodes(tree_widget_item.child(i)))
    return nodes

def get_all_tree_items(tree_widget):
    """Returns all QTreeWidgetItems in the given QTreeWidget."""
    all_items = list()
    for i in range(tree_widget.topLevelItemCount()):
        top_item = tree_widget.topLevelItem(i)
        all_items.extend(get_subtree_nodes(top_item))
    return all_items
###############################################################################

utility_nodes = ['parentConstraint', 'orientConstraint', 'scaleConstraint', 'pointConstraint', 'aimConstraint',
                 'addDoubleLinear', 'addMatrix', 'angleBetween',
                 'composeMatrix', 'condition', 'decomposeMatrix',
                 'distanceBetween', 'floatComposite', 'floatCondition',
                 'floatConstant', 'floatCorrect', 'floatLogic', 'floatMask', 'floatMath', 'fourByFourMatrix',
                 'inverseMatrix',
                 'multDoubleLinear', 'multMatrix', 'multiplyDivide',
                 'plusMinusAverage', 'premultiply', 'projection',
                 'remapColor', 'remapHsv', 'remapValue', 'reverse',
                 'setRange',
                 'transposeMatrix', 'tripleShadingSwitch', 'unitConversion', 'unpremultiply', 'vectorProduct',
                 'wtAddMatrix']

