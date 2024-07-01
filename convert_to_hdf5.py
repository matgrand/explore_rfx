#!/usr/bin/env python
import MDSplus as mds
from tqdm import tqdm
import h5py as h5
import numpy as np

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
    
def time2range(v:np.ndarray):
    #convert a 1d vector of time into the 3 parameters of a range
    assert isinstance(v, np.ndarray) and len(v) > 1 and v.ndim == 1, f'wrong input: {v}'
    s, e = v[0], v[-1] # start and end of the time vector
    assert s < e, f'start:{s} >= end:{e}'
    v1 = np.linspace(s, e, len(v)) 
    # v1 = np.arange(s, e, (e-s)/(len(v)))
    s1, e1 = v1[0], v1[-1]
    assert np.allclose(s1, s) and np.allclose(e1, e), f'start!=end: {s1} != {s} or {e1} != {e}'
    diff0, diff1 = np.diff(v), np.diff(v1)
    stdd0, stdd1 = np.std(diff0), np.std(diff1)
    assert np.allclose(v, v1), f'not a range: d:{v[1]-v[0]}, d0:{v[1]-v[0]}  norm:{np.linalg.norm(v-v1)}, std0:{stdd0}, std1:{stdd1}'
    return s, e, len(v)

# let's do the same but without recursion
MAX_DEPTH = 12

def convert_mds_tree2hdf(hdf:h5.File, start_node=None, only_raw=True, videos=False, max_depth=4):
    curr_nodes = [start_node]
    for d in range(max_depth):
        next_nodes = []
        for node in tqdm(curr_nodes, desc=f'Depth {d}:', ncols=80):
            # GET STUFF ABOUT THE NODE
            npath = str(node.getFullPath()) # full path of the node in the tree
            if npath in SEG_FAULT_NODES: continue # skip the nodes that cause seg faults
            npath = npath[10:].replace('.', '/').replace(':', '/') # remove the first 10 characters and replace . and : with /
            length = node.length # length of data in bytes, uncompressed
            if length > 10_000_000: print(f'{WARN}NODE {npath} has length {length}{ENDC}')
            is_child = node.isChild() 
            is_member = node.isMember()
            has_children = hasChildren(node)
            has_members = hasMembers(node)
            has_time = hasTime(node)
            has_data = hasData(node)
            ndata = node.data() if has_data else None
            ntime = node.dim_of().data() if has_time else None
            nname = node.node_name.upper() # name of the node
            nusage = str(node.usage).upper() # usage of the node: SIGNAL, STRUCTURE, NUMERIC, etc.
            
            # CHECK LOGIC INTEGRITY + DATA CLEANING
            # assert->very important, ERROR->less important, WARN->not important
            assert (is_child or is_member) and not (is_child and is_member) # can't be both child and member
            # check if there is 'video' in the name
            if videos and nname.lower().find('video') > -1: 
                print(f'{ERR}NODE {npath} has VIDEO in the name, skipping{ENDC}')
                continue # skip the nodes that have 'video' in the name
            # check children and members data logic integrity
            if has_data and has_children: 
                print(f'{WARN}NODE {npath} has DATA and CHILDREN: data: {node.data()}, CHILDREN: {node.getChildren()}{ENDC}')
            if has_data and has_members: 
                print(f'{WARN}node {npath} has data and members: data: {node.data()}, members: {node.getMembers()}{ENDC}')
            # check signal logic integrity
            if nusage == 'SIGNAL' and not (has_data and has_time): 
                print(f'{ERR}NODE {npath} is a SIGNAL but has no data or time{ENDC}')
                continue # skip signal nodes that have no data or time
            if has_data and has_time:
                if len(ndata) == len(ntime): nusage = 'SIGNAL'# it is actually a signal
                else: # different lengths of data and time -> not signal or bad signal
                    print(f'{ERR}NODE {npath} has data and time but different lengths: {len(ndata)} != {len(ntime)}{ENDC}')
                    continue # skip the nodes that have different lengths of data and time
            # a signal is a signal if and only if it has data and time and the lengths are the same
            if has_data and has_time and len(ndata) == len(ntime): assert nusage == 'SIGNAL'
            if nusage == 'SIGNAL': assert has_data and has_time and len(ndata) == len(ntime)
            
            #keep only raw signals
            if only_raw and nusage == 'SIGNAL' and npath.lower().find('raw') == -1: 
                print(f'{OK}NODE {npath} is SIGNAL but not RAW, skipping{ENDC}')
                continue
            
            # BUILD THE HDF5 TREE
            if has_children or has_members: 
                group = hdf.create_group(npath)  
                group.attrs['usage'] = nusage  
            
            if has_data: # save the data to the hdf5 file
                if has_time: # is a signal
                    try:
                        ds = hdf.create_dataset(npath, data=ndata)
                        ds.attrs['dtype'] = str(ndata.dtype)
                        ds.attrs['usage'] = nusage
                        ds.attrs['time_range'] = time2range(ntime)
                    except Exception as e:
                        print(f'{ERR}NODE {npath} is SIGNAL but failed to save: {e}\ndata:{ndata}, time:{ntime}{ENDC}')
                else: # not signal: text, numeric
                    dtype = str(ndata.dtype)
                    if dtype.startswith('<U'): ndata = str(ndata)
                    try:
                        ds = hdf.create_dataset(npath, data=ndata)
                        ds.attrs['dtype'] = dtype
                        ds.attrs['usage'] = nusage
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
    np.set_printoptions(precision=4, suppress=True)
    
    rfx = mds.Tree('rfx', SHOT, 'readonly') # open the tree read-only
    # HEAD_NODE = rfx.getNode('\\TOP.RFX')    
    HEAD_NODE = rfx.getNode('\\TOP.RFX.MHD')    
    # HEAD_NODE = rfx.getNode('\\TOP.RFX.EDA')    

    with h5.File(HDF5_FILE, 'w') as f:
        convert_mds_tree2hdf(f, HEAD_NODE, only_raw=False, videos=False, max_depth=MAX_DEPTH) 
        # h5_tree(f) # print the tree structure