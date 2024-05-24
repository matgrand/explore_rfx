# print tree structure
import MDSplus as mds
import os

def traverse_tree(node, level=0):
    print('  ' * level + node.node_name) # print the name of the node 
    children = node.getChildren() # get the children of the node
    members = node.getMembers() # get the members of the node
    for child in children:
        try: traverse_tree(child, level + 1)
        except: pass
    for member in members:
        try: traverse_tree(member, level + 1)
        except: pass
        
rfx = mds.Tree('rfx', 30810, 'readonly')
traverse_tree(rfx.getNode('\\TOP')) # start the traversal at the top node