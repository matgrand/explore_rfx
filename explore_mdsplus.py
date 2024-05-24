# print tree structure
import MDSplus as mds
import os

rfx = mds.Tree('rfx', 30810, 'readonly') # open the tree

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

# traverse_tree(rfx.getNode('\\TOP')) # start the traversal at the top node

# do the same but without recursion
MAX_DEPTH = 3
curr_nodes = [rfx.getNode('\\TOP')]
for d in range(MAX_DEPTH):
    print('Depth:', d)
    next_nodes = []
    for node in curr_nodes:
        print(node.node_name)
        next_nodes += node.getChildren() + node.getMembers()
    curr_nodes = next_nodes