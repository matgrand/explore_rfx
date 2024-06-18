#!/usr/bin/env python
# coding: utf-8

# # Let's explore the RFX MDSplus tree

# ## Importing and setting up stuff

# In[ ]:


import MDSplus as mds
import numpy as np
import matplotlib.pyplot as plt
import sys, os, time, random
from tqdm import tqdm
import h5py as h5
print(f'Python version: {sys.version}')
print(f'MDSplus version: {mds.__version__}')
np.set_printoptions(precision=3, suppress=True)


# In[ ]:


#color the terminal output
def pick_random_color():
    return '\033[38;5;{}m'.format(random.randint(8, 230))
ENDC = '\033[0m'
ERR = '\033[91m'+ 'ERR: '
OK = '\033[92m' 
WARN = '\033[93m'+ 'WARN: '


# In[ ]:


# define the shot number and tree
SHOT = 30810
rfx = mds.Tree('rfx', SHOT, 'readonly') # open the tree read-only


# In[ ]:


SEG_FAULT_NODES = [
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_1:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_10:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_3:SPECIAL_GATE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:REPEAT_COUNT',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:SPECIAL_GATE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_01:VOLTAGES',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_01:TIME_MODE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:LOAD',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_02:OUTPUT',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_02:VOLTAGES',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_11:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_12:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_2:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_3:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_4:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_5:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_6:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_7:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_8:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_9:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:TIMING:DIO2_1.CHANNEL_1:CLOCK',
]


# ## Traversing the tree

# In[ ]:


# traverse the tree, use MAX_DEPTH to limit the depth of the tree to traverse
# othwerwise the script will run for about 10 minutes
MAX_DEPTH = 13 # maximum depth of the tree to traverse
COLORS = [pick_random_color() for i in range(MAX_DEPTH)]

usage_depth, usage_breadth = {},{}
total_nodes_depth, total_nodes_breadth = [],[]

def traverse_tree_depth_first(max_depth, node, level=0, path='', node_type='child'):
    try: 
        if level >= max_depth: return # stop if the maximum depth is reached
        if node.getFullPath() in SEG_FAULT_NODES: return # skip the nodes that cause segfault
        if node_type == 'child': node_name = node.node_name.upper()
        elif node_type == 'member': node_name = node.node_name.lower()
        else: raise
        path = path + '/' + COLORS[level] + node_name + ENDC # add the node name
        total_nodes_depth.append(node) # add the node to the list
        print(f'{path}:{node.decompile()}') 
        # get the usage/type of the node
        try: usage_depth[str(node.usage)] += 1
        except: usage_depth[str(node.usage)] = 1
        # go through the children and members of the node
        for child in node.getChildren(): # get the children of the node
            traverse_tree_depth_first(max_depth, child, level + 1, path, 'child')
        for member in node.getMembers(): # get the members of the node
            traverse_tree_depth_first(max_depth, member, level + 1, path, 'member')
    except Exception as e:
        print(path + 'ERR:' + str(e))
        pass

# do the same but without recursion
def traverse_tree_breadth_first(max_depth, head_node):
    curr_nodes = [head_node]
    for d in range(max_depth):
        print('Depth:', d)
        next_nodes = []
        for node in curr_nodes:
            try:
                if node.getFullPath() in SEG_FAULT_NODES: continue # skip the nodes that cause segfault
                preprint = COLORS[d] + "   " * d + node.node_name + ENDC
                print(f'{preprint}:{node.decompile()}') # print the node
                total_nodes_breadth.append(node) # add the node to the list
                # get the usage/type of the node
                try: usage_breadth[str(node.usage)] += 1
                except: usage_breadth[str(node.usage)] = 1
                # get the children of the node
                for child in node.getChildren():
                    next_nodes.append(child)
                # get the members of the node
                for member in node.getMembers():
                    next_nodes.append(member)
            except: pass
        curr_nodes = next_nodes
        
head_node = rfx.getNode('\\TOP.RFX') # get the top node

# # test the functions, uncomment to run
# traverse_tree_depth_first(MAX_DEPTH, head_node) # traverse the tree depth-first
# traverse_tree_breadth_first(MAX_DEPTH, head_node) # traverse the tree breadth-first

# print(f'Total nodes depth: {len(total_nodes_depth)}') # 96771, 96750
# print(f'Total nodes breadth: {len(total_nodes_breadth)}') # 96771, 96750


# In[ ]:


print(f'Usage depth: {usage_depth}')
print(f'Usage breadth: {usage_breadth}')


# previous cell full depth: 'STRUCTURE': 8776, 'SUBTREE': 78, 'DEVICE': 642, 'ACTION': 1098, 'NUMERIC': 47760, 'TEXT': 17269, 'SIGNAL': 20904, 'ANY': 29, 'AXIS': 215

# In[ ]:


print(f'top nodes: {[n.node_name for n in head_node.getChildren()]}')


# ## Exploring Signals

# In[ ]:


search_space = '\\TOP.RFX.MHD.***' # *** means all nodes at this level
# search_space = '\\TOP.RFX.EDA.***' # * means all nodes at this level
# search_space = '\\TOP.RFX.***' # whole rfx tree
signal_nodes = rfx.getNodeWild(search_space, 'Signal') # get all nodes with the name 'Signal'
print(f'Found {len(signal_nodes)} of the type Signal in the search space {search_space}')


# In[ ]:


# # filter out the nodes without the data
# data_signals = []
# for node in tqdm(signal_nodes, leave=False):
#     try: data = node.data(); data_signals.append(node)
#     except: pass
# print(f'Found {len(data_signals)}/{len(signal_nodes)} signals with data')


# In[ ]:


# # keep only the signals with raw data
# raw_signals = []
# for node in tqdm(signal_nodes, leave=False):
#     try: data = node.raw_of().data(); raw_signals.append(node)
#     except: pass
# print(f'Found {len(raw_signals)}/{len(data_signals)} signals with raw data')


# In[ ]:


# # extract data from the signals and plot them
# MAX_LOAD = 0 #10 #np.inf
# MAX_LOAD = min(MAX_LOAD, len(raw_signals))
# # select MAX_LOAD random signals
# signals = random.sample(raw_signals, MAX_LOAD)
# for node in (signals):
#     signal = node.data()
#     times = node.dim_of().data()
#     unit = node.getUnits()
#     full_path = node.getFullPath()
#     try: node_help = node.getHelp()
#     except: node_help = ''
#     if signal.shape != times.shape:
#         print(f'{full_path} has mismatched signal and time shapes')
#         continue
#     # plot the signal
#     plt.figure()
#     plt.plot(times, signal)
#     plt.title(f'{full_path} [{unit}]\n{node_help}')
#     plt.xlabel('Time [s]')
#     plt.ylabel('Signal')
#     plt.show()


# ## Exploring Text

# In[ ]:


# text_nodes = rfx.getNodeWild(search_space, 'Text') # get all the 'TEXT' nodes
# print(f'Found {len(text_nodes)} of the type Text in the search space {search_space}')
# # print all the text nodes
# for node in text_nodes:
#     try: print(f'{node.getFullPath()}={node.data()}')
#     except: pass


# ## Convert tree in HDF5 format

# In[ ]:


HDF5_FILE = f'rfx_{SHOT}.hdf5'


# In[ ]:


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


# In[ ]:


# define a list of nodes to skip, because they trow segmentation fault
SEG_FAULT_NODES = [
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_1:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_10:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_3:SPECIAL_GATE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:REPEAT_COUNT',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:SPECIAL_GATE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_01:VOLTAGES',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_01:TIME_MODE',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:DECODER_01.CHANNEL_5:LOAD',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_02:OUTPUT',
    '\\RFX::TOP.RFX.DIAG.DTER.DTER_RAW.TIMING:K3115_01.CHANNEL_02:VOLTAGES',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_11:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_12:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_2:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_3:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_4:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_5:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_6:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_7:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_8:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:ADC:TR10_9:CLOCK_SOURCE',
    '\\RFX::TOP.RFX.MHD.MHD_BR:CPCI_1:TIMING:DIO2_1.CHANNEL_1:CLOCK',
]

# check that the nodes exist
for snpath in SEG_FAULT_NODES:
    try: n = rfx.getNode(snpath); assert snpath == str(n.getFullPath())
    except: print(f'{snpath} does not exist')


# In[ ]:


# let's do the same but without recursion
MAX_DEPTH = 12
with h5.File(HDF5_FILE, 'w') as hdf:
    skipped_nodes = 0
    def explore_tree(start_node=rfx.getNode('\\TOP.RFX'), max_depth=4):
        curr_nodes = [start_node]
        for d in range(max_depth):
            next_nodes = []
            for node in tqdm(curr_nodes, desc=f'Depth {d}:', ncols=80):
            # for node in curr_nodes:
                npath = str(node.getFullPath())
                # print(f'{npath}')
                if npath in SEG_FAULT_NODES: print(f'{ERR}Skipping {npath}{ENDC}'); continue
                npath = npath[10:].replace('.', '/').replace(':', '/')
                length = node.length # length of data in bytes, uncompressed
                if length > 10_000_000: print(f'{WARN}NODE {npath} has length {length}{ENDC}')
                
                is_child = node.isChild()
                is_member = node.isMember()
                assert (is_child or is_member) and not (is_child and is_member)
                has_children = hasChildren(node)
                has_members = hasMembers(node)
                has_time = hasTime(node)
                has_data = hasData(node)
                nname = node.node_name.upper() if is_child else node.node_name.lower()
                nusage = str(node.usage)
                
                if has_children or has_members: 
                    group = hdf.create_group(npath)  
                    group.attrs['usage'] = nusage  
                    
                if has_data and has_children: print(f'{ERR}NODE {npath} has DATA and CHILDREN: data: {node.data()}, CHILDREN: {node.getChildren()}{ENDC}')
                if has_data and has_members: print(f'{WARN}node {npath} has data and members: data: {node.data()}, members: {node.getMembers()}{ENDC}')
                
                if has_data: # save the data to the hdf5 file
                    data = node.data()
                    try:
                        hdf.create_dataset(npath, data=data)
                        # hdf.create_dataset(f'{npath}/dataset', data=0)
                    except Exception as e:
                        print(f'{ERR}NODE {npath} has data but failed to save: {e}{ENDC}')
                
                if has_children:
                    for child in node.getChildren(): next_nodes.append(child)
                if has_members:
                    for member in node.getMembers(): next_nodes.append(member)                
            curr_nodes = next_nodes

    # top_nodes = ["MHD.MHD_BR","MHD", "SETUP", "STC", "VERSIONS"]
    # for tn in top_nodes:
    #     print(f'\nTop node: {tn}\n')
    #     explore_tree(rfx.getNode(f'\\TOP.RFX.{tn}'), MAX_DEPTH)
    #     print(f'\n{tn} FINISHED\n=================================\n=================================\n=================================\n')
    
    explore_tree(rfx.getNode('\\TOP.RFX'), MAX_DEPTH)    
                                


# In[ ]:


# print the tree structure
tot_nodes_hdf5 = []
def h5_tree(vals, pre='', mid_syms=('├────','│     '), end_syms=('└────','      ')):
    for i, (key, val) in enumerate(vals.items()):
        s1, s2 = end_syms if i == len(vals)-1 else mid_syms
        tot_nodes_hdf5.append(key)
        if type(val) == h5.Group: 
            print(f'{pre}{s1} {key}') 
            h5_tree(val, f'{pre}{s2}', mid_syms, end_syms)
        else: print(f'{pre}{s1} {key} [{val.shape} {val.dtype}]')


# In[ ]:


with h5.File(HDF5_FILE, 'r') as f: 
    h5_tree(f)
    # print the total number of nodes in the hdf5 file
    print(f'Total nodes in the HDF5 file: {len(tot_nodes_hdf5)}') # 77395, 145291

