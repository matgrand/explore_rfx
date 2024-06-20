#!/usr/bin/env python
import MDSplus as mds
from tqdm import tqdm
import h5py as h5

# terminal output colors
ENDC = '\033[0m'
ERR = '\033[91m'+ 'ERR: '
OK = '\033[92m' 
WARN = '\033[93m'+ 'WARN: '

# define the shot number and tree
SHOT = 30810
HDF5_FILE = f'rfx_{SHOT}.hdf5'

SEG_FAULT_NODES = [ # these are the nodes that cause a seg fault when loading something from them
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
MAX_DEPTH = 12

def convert_mds_tree2hdf(hdf:h5.File, start_node=None, max_depth=4):
    curr_nodes = [start_node]
    for d in range(max_depth):
        next_nodes = []
        for node in tqdm(curr_nodes, desc=f'Depth {d}:', ncols=80):
        # for node in curr_nodes:
            npath = str(node.getFullPath())
            # print(f'{npath}')
            if npath in SEG_FAULT_NODES: continue # skip the nodes that cause seg faults
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
            
            # check if there is 'video' in the name
            if nname.lower().find('video') > -1: print(f'{ERR}NODE {npath} has VIDEO in the name, skipping{ENDC}'); continue
            
            if has_children or has_members: 
                group = hdf.create_group(npath)  
                group.attrs['usage'] = nusage  
            
            if has_data and has_children: print(f'{ERR}NODE {npath} has DATA and CHILDREN: data: {node.data()}, CHILDREN: {node.getChildren()}{ENDC}')
            if has_data and has_members: print(f'{WARN}node {npath} has data and members: data: {node.data()}, members: {node.getMembers()}{ENDC}')
            
            if has_data: # save the data to the hdf5 file
                data = node.data()
                dtype = str(data.dtype)
                if dtype.startswith('<U'): data = str(data)
                try:
                    ds = hdf.create_dataset(npath, data=data)
                    ds.attrs['dtype'] = dtype
                    ds.attrs['usage'] = nusage
                    # hdf.create_dataset(f'{npath}/dataset', data=0)
                except Exception as e:
                    print(f'{ERR}NODE {npath} has data but failed to save: {e}\ndtype:{dtype}, length:{length}, \ndata:{data}{ENDC}')
            
            if has_children:
                for child in node.getChildren(): next_nodes.append(child)
            if has_members:
                for member in node.getMembers(): next_nodes.append(member)                
        curr_nodes = next_nodes

# print the tree structure
tot_nodes_hdf5 = []
def h5_tree(tree, pre='', mid_syms=('├────','│     '), end_syms=('└────','      ')):
    for i, (key, val) in enumerate(tree.items()):
        s1, s2 = end_syms if i == len(tree)-1 else mid_syms
        tot_nodes_hdf5.append(key)
        if type(val) == h5.Group: 
            print(f'{pre}{s1} {key}') 
            h5_tree(val, f'{pre}{s2}', mid_syms, end_syms)
        else: 
            shape = val.shape if val is not None else None
            dtype = val.dtype if val is not None else None
            usage = val.attrs.get('usage', None)
            print(f'{pre}{s1} {key} [{shape} {dtype}] {usage}')

if __name__ == '__main__':    
    print(f'MDSplus version: {mds.__version__}')
    
    rfx = mds.Tree('rfx', SHOT, 'readonly') # open the tree read-only
    HEAD_NODE = rfx.getNode('\\TOP.RFX')    
    # HEAD_NODE = rfx.getNode('\\TOP.RFX.MHD')    
    # HEAD_NODE = rfx.getNode('\\TOP.RFX.MHD')    

    with h5.File(HDF5_FILE, 'w') as f:
        convert_mds_tree2hdf(f, HEAD_NODE, MAX_DEPTH)    
    
    with h5.File(HDF5_FILE, 'r') as f: 
        h5_tree(f)