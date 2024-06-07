# print tree structure
import MDSplus as mds
import os
import random
from time import time, sleep
print('\n'*1000)
os.system('clear')
print('MDSplus version:', mds.__version__)

MAX_DEPTH = 20 # maximum depth to traverse the tree

#color the terminal output
def pick_random_color():
    return '\033[38;5;{}m'.format(random.randint(8, 230))
COLORS = [pick_random_color() for i in range(MAX_DEPTH)]
ENDC = '\033[0m'
        
def traverse_tree_depth_first(node, level=0, path='', node_type='child'):
    try: 
        if level >= MAX_DEPTH: return # stop if the maximum depth is reached
        if node_type == 'child': node_name = node.node_name.upper()
        elif node_type == 'member': node_name = node.node_name.lower()
        else: raise ValueError('node_type must be either "child" or "member"') 
        path = path + '/' + COLORS[level] + node_name + ENDC # add the node name
        print(f'{path}:{node.decompile()}') 
        # go through the children and members of the node
        for child in node.getChildren(): # get the children of the node
            traverse_tree_depth_first(child, level + 1, path, 'child')
        for member in node.getMembers(): # get the members of the node
            traverse_tree_depth_first(member, level + 1, path, 'member')
    except Exception as e:
        print(path + 'ERR:' + str(e))
        pass

# do the same but without recursion
def traverse_tree_breadth_first(head_node):
    curr_nodes = [head_node]
    for d in range(MAX_DEPTH):
        print('Depth:', d)
        next_nodes = []
        for node in curr_nodes:
            try:
                preprint = COLORS[d] + "   " * d + node.node_name + ENDC
                print(f'{preprint}:{node.decompile()}') # print the node
                # get the children of the node
                for child in node.getChildren():
                    next_nodes.append(child)
                # get the members of the node
                for member in node.getMembers():
                    next_nodes.append(member)
            except: pass
        curr_nodes = next_nodes
            
def explore_signals(head_node='\\TOP.RFX.MHD.***'):
    # get all the nodes with data
    data_nodes = rfx.getNodeWild(head_node, 'Signal')
    assert len(data_nodes) > 0, 'No data nodes found'
    data_nodes_names = [dn.node_name for dn in data_nodes]
    for dn, dnn in zip(data_nodes, data_nodes_names):
        got_data = False
        try: 
            d = dn.getData()
            got_data = True
            raw = d.raw_of()
            if raw is not None: raw = raw[:10]
            times = d.dim_of()
            unit = d.units_of()
            value = d.value_of()
            raw_type = type(raw)
            rc = pick_random_color()
            
            print(f'{rc}{dnn}: {raw_type}|{raw}|{times}|{unit}|{value}{ENDC}')
        except Exception as e: 
            pass
            assert not got_data, 'Data was not retrieved'
            print(dnn + ' err:' + str(e))

if __name__ == '__main__':
    rfx = mds.Tree('rfx', 30810, 'readonly') # open the tree read-only
    # rfx = mds.Tree('rfx', 30810) # open the tree

    # head_node = rfx.getNode('\\TOP') # get the top node
    head_node = rfx.getNode('\\TOP.RFX') # get the top node
        
    # traverse_tree_depth_first(head_node) # start the traversal at the top node
    # traverse_tree_breadth_first(head_node) # start the traversal at the top node
    explore_signals('\\TOP.RFX.MHD.***') 


    # close the tree
    rfx.close()





