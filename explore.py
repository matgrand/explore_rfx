import MDSplus as mds
import numpy as np
import matplotlib.pyplot as plt
import sys, os, time, random
from tqdm import tqdm
import h5py as h5
print(f'Python version: {sys.version}')
print(f'MDSplus version: {mds.__version__}')
np.set_printoptions(precision=3, suppress=True)

#color the terminal output
def pick_random_color():
    return '\033[38;5;{}m'.format(random.randint(8, 230))
ENDC = '\033[0m'
ERR = '\033[91m'+ 'ERR: '
OK = '\033[92m'
WARN = '\033[93m'+ 'WARN: '

# define the shot number and tree
SHOT = 30810
rfx = mds.Tree('rfx', SHOT, 'readonly') # open the tree read-only

HDF5_FILE = f'rfx_{SHOT}.hdf5'

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
    
# let's do the same but without recursion
MAX_DEPTH = 8

# with h5.File(HDF5_FILE, 'w') as hdf:
def explore_tree(max_depth):
    curr_nodes = [(rfx.getNode('\\TOP.RFX'),'child')]
    for d in range(max_depth):
        next_nodes = []
        print(f'Depth: {d}')
        # for node, node_type in tqdm(curr_nodes, desc=f'Depth {d}:', ncols=80):
        for node, node_type in curr_nodes:
            is_child = node.isChild()
            is_member = node.isMember()
            assert (is_child or is_member) and not (is_child and is_member) # check if the node is either a child or a member
            has_children = hasChildren(node)
            has_members = hasMembers(node)
            has_time = hasTime(node)
            has_data = hasData(node)
            nname = node.node_name.upper() if is_child else node.node_name.lower()
            npath = str(node.getFullPath())
            nusage = str(node.usage)
            
            path = npath[10:].replace('.', '/').replace(':', '/')
            # if has_children or has_members: 
            #     group = hdf.create_group(path)  
            #     group.attrs['usage'] = nusage  
                
            if has_data and has_children: print(f'{ERR}NODE {path} has DATA and CHILDREN: data: {node.data()}, CHILDREN: {node.getChildren()}{ENDC}')
            if has_data and has_members: print(f'{WARN}node {path} has data and members: data: {node.data()}, members: {node.getMembers()}{ENDC}')
            
            # if has_data: # save åçthe data to the hdf5 file
            #     data = node.data()
            #     hdf.create_dataset(path, data=data)
            
            if has_children:
                for child in node.getChildren(): next_nodes.append((child, 'child'))
            if has_members:
                for member in node.getMembers(): next_nodes.append((member, 'member'))                
            
        curr_nodes = next_nodes
            
explore_tree(MAX_DEPTH)    
    
    
#     # print the tree structure
# def h5_tree(vals, pre='', mid_syms=('├────','│     '), end_syms=('└────','      ')):
#     for i, (key, val) in enumerate(vals.items()):
#         s1, s2 = end_syms if i == len(vals)-1 else mid_syms
#         if type(val) == h5.Group: 
#             print(f'{pre}{s1} {key}') 
#             h5_tree(val, f'{pre}{s2}', mid_syms, end_syms)
#         else: print(f'{pre}{s1} {key} [{val.shape} {val.dtype}]')

# with h5.File(HDF5_FILE, 'r') as f: h5_tree(f)
