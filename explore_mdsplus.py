# print tree structure
import MDSplus as mds
import os
import random

print('MDSplus version:', mds.__version__)

rfx = mds.Tree('rfx', 30810, 'readonly') # open the tree

# head_node = rfx.getNode('\\TOP') # get the top node
head_node = rfx.getNode('\\TOP.RFX') # get the top node

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

# traverse_tree(head_node) # start the traversal at the top node

# do the same but without recursion
def traverse_tree2(head_node, max_depth=10):
    # define max_depth random terminal colors
    colors = ['\e[38;5;{}m'.format(random.randint(0, 255)) for _ in range(max_depth)]
    ec = '\033[0m' # end color
    # for _ in range(max_depth):
    #     colors.append('\e[38;5;{}m'.format(random.randint(0, 255)))
    curr_nodes = [head_node]
    for d in range(max_depth):
        print('Depth:', d)
        next_nodes = []
        for node in curr_nodes:
            print(colors[d] + "   " * d + node.node_name + ec)

            # get data in the node (if any)
            try:
                data = node.data 
                print(colors[d] + "   " * d + str(data) + ec)
            except:
                print(colors[d] + "   " * d + "_____________" + ec)

            # get the children of the node
            try:
                for child in node.getChildren():
                    next_nodes.append(child)
            except: pass
        curr_nodes = next_nodes

traverse_tree2(head_node, 5) # start the traversal at the top node
