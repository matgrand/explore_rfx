# print tree structure
import MDSplus as mds
import os
import random

print('MDSplus version:', mds.__version__)

MAX_DEPTH = 9 # maximum depth to traverse the tree

rfx = mds.Tree('rfx', 30810, 'readonly') # open the tree read-only
# rfx = mds.Tree('rfx', 30810) # open the tree

# head_node = rfx.getNode('\\TOP') # get the top node
head_node = rfx.getNode('\\TOP.RFX') # get the top node

#color the terminal output
COLORS = ['\033[38;5;{}m'.format(random.randint(8, 230)) for _ in range(MAX_DEPTH)]
ENDC = '\033[0m'


def print_node(node, preprint=''):
    try:
        data = node.decompile()
        # data = vars(node)
        print(preprint + ':' + str(data))
    except Exception as e:
        print(preprint + node.node_name + 'ERR:' + str(e))

def traverse_tree(node, level=0, path='', node_type='child'):
    if level >= MAX_DEPTH: return # stop if the maximum depth is reached
    if node_type == 'child': node_name = node.node_name.upper()
    elif node_type == 'member': node_name = node.node_name.lower()
    else: raise ValueError('node_type must be either "child" or "member"') 
    path = path + '/' + COLORS[level] + node.node_name + ENDC
    # print(path)
    print_node(node, path)
    
    # go through the children and members of the node
    children = node.getChildren() # get the children of the node
    members = node.getMembers() # get the members of the node
    for child in children:
        try: traverse_tree(child, level + 1, path, 'child')
        except: pass
    for member in members:
        try: traverse_tree(member, level + 1, path, 'member')
        except: pass        

# do the same but without recursion
def traverse_tree2(head_node):
    curr_nodes = [head_node]
    for d in range(MAX_DEPTH):
        print('Depth:', d)
        next_nodes = []
        for node in curr_nodes:
            preprint = COLORS[d] + "   " * d + node.node_name + ENDC
            print(preprint)
            print_node(node, preprint)
            
            # get the children of the node
            try:
                for child in node.getChildren():
                    next_nodes.append(child)
            except: pass
        curr_nodes = next_nodes

if __name__ == '__main__':

    traverse_tree(head_node) # start the traversal at the top node
    print('\n' * 10) # add some space
    # traverse_tree2(head_node) # start the traversal at the top node
