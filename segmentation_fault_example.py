import MDSplus as mds
import numpy as np
import sys
from tqdm import tqdm
print(f'Python version: {sys.version}')
print(f'MDSplus version: {mds.__version__}')

# colors 
ENDC = '\033[0m'
ERR = '\033[91m'+ 'ERR: '
OK = '\033[92m'
WARN = '\033[93m'+ 'WARN: '

# define the shot number and tree
SHOT = 30810
rfx = mds.Tree('rfx', SHOT, 'readonly') # open the tree read-only

# functions to check if the node has data, time, children or members
def hasData(node):
    try: _ = node.data(); return True
    except: return False

def hasTime(node):
    try: _ = node.dim_of().data(); return True
    except: return False
    
def hasChildren(node):
    try: return len(node.getChildren()) > 0
    except: return False

def hasMembers(node):
    try: return len(node.getMembers()) > 0
    except: return False

def explore_tree(max_depth):
    curr_nodes = [rfx.getNode('\\TOP.RFX')]
    for d in range(max_depth):
        next_nodes = []
        print(f'Depth: {d}')
        for node in curr_nodes:
            npath = str(node.getFullPath())
            npath = npath[10:]#.replace('.', '/').replace(':', '/')
            print(npath)
            
            is_child = node.isChild()
            is_member = node.isMember()
            assert (is_child or is_member) and not (is_child and is_member) # check if the node is either a child or a member
            has_children = hasChildren(node)
            has_members = hasMembers(node)
            has_time = hasTime(node)
            has_data = hasData(node)
            nname = node.node_name.upper() if is_child else node.node_name.lower()
            nusage = str(node.usage)
                
            if has_data and has_children: print(f'{ERR}NODE {npath} has DATA and CHILDREN: data: {node.data()}, CHILDREN: {node.getChildren()}{ENDC}')
            if has_data and has_members: print(f'{WARN}node {npath} has data and members: data: {node.data()}, members: {node.getMembers()}{ENDC}')

            if has_children:
                for child in node.getChildren(): next_nodes.append(child)
            if has_members:
                for member in node.getMembers(): next_nodes.append(member)                
            
        curr_nodes = next_nodes
            
explore_tree(8)    