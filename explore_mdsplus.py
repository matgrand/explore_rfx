# print tree structure
import MDSplus as mds
import os
import random

print('MDSplus version:', mds.__version__)

MAX_DEPTH = 5 # maximum depth to traverse the tree

rfx = mds.Tree('rfx', 30810, 'readonly') # open the tree

# head_node = rfx.getNode('\\TOP') # get the top node
head_node = rfx.getNode('\\TOP.RFX') # get the top node

#color the terminal output
COLORS = ['\033[38;5;{}m'.format(random.randint(0, 231)) for _ in range(MAX_DEPTH)]
ENDC = '\033[0m'

def traverse_tree(node, level=0, path=''):
    if level >= MAX_DEPTH: return # stop if the maximum depth is reached
    path = path + '/' + COLORS[level] + node.node_name + ENDC
    # print(COLORS[level] + '   ' * level + node.node_name + ENDC) # print the name of the node 
    print(path)
    children = node.getChildren() # get the children of the node
    members = node.getMembers() # get the members of the node
    for child in children:
        try: traverse_tree(child, level + 1, path)
        except: pass
    for member in members:
        try: traverse_tree(member, level + 1, path)
        except: pass        

traverse_tree(head_node) # start the traversal at the top node

print('\n' * 10) # add some space

# do the same but without recursion
def traverse_tree2(head_node):
    curr_nodes = [head_node]
    for d in range(MAX_DEPTH):
        print('Depth:', d)
        next_nodes = []
        for node in curr_nodes:
            print(COLORS[d] + "   " * d + node.node_name + ENDC)

            # get data in the node (if any)
            try:
                data = node.data 
                print(COLORS[d] + "   " * d + str(data) + ENDC)
            except:
                print(COLORS[d] + "   " * d + "_____________" + ENDC)

            # get the children of the node
            try:
                for child in node.getChildren():
                    next_nodes.append(child)
            except: pass
        curr_nodes = next_nodes

# traverse_tree2(head_node) # start the traversal at the top node
