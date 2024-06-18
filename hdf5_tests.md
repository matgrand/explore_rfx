```python
import h5py as h5
import numpy as np
import random
```


```python
# create a random hdf5 tree
def create_random_hdf5_tree(max_depth, max_children, max_members, max_datasets, hdf5_file):
    with h5.File(hdf5_file, 'w') as f:
        def create_random_group(group, depth=0):
            if depth >= max_depth: return
            n_children = random.randint(1, max_children)
            n_members = random.randint(1, max_members)
            n_datasets = random.randint(1, max_datasets)
            for i in range(n_children):
                child = group.create_group(f'child_{i}')
                create_random_group(child, depth + 1)
            for i in range(n_members):
                member = group.create_group(f'member_{i}')
                create_random_group(member, depth + 1)
            for i in range(n_datasets):
                data = np.random.rand(3, 3)
                if np.random.rand() < 0.5: data = 'test_string'
                group.create_dataset(f'dataset_{i}', data=data)
        create_random_group(f)

# test the function
create_random_hdf5_tree(3, 2, 2, 2, 'random.hdf5')
```


```python
# print the tree structure
def h5_tree(vals, pre='', mid_syms=('├──','│   '), end_syms=('└──','    ')):
    for i, (key, val) in enumerate(vals.items()):
        s1, s2 = end_syms if i == len(vals)-1 else mid_syms
        if type(val) == h5.Group: 
            print(f'{pre}{s1} {key}') 
            h5_tree(val, f'{pre}{s2}', mid_syms, end_syms)
        else: print(f'{pre}{s1} {key} [{val.shape} {val.dtype}]')
# with h5.File(HDF5_FILE, 'r') as f: h5_tree(f)
with h5.File('random.hdf5', 'r') as f: h5_tree(f)
```

    ├── child_0
    │   ├── child_0
    │   │   ├── child_0
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   ├── member_0
    │   │   └── member_1
    │   ├── dataset_0 [() object]
    │   ├── dataset_1 [() object]
    │   └── member_0
    │       ├── child_0
    │       ├── child_1
    │       ├── dataset_0 [() object]
    │       └── member_0
    ├── child_1
    │   ├── child_0
    │   │   ├── child_0
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   ├── child_1
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [(3, 3) float64]
    │   │   └── member_0
    │   ├── dataset_0 [() object]
    │   ├── member_0
    │   │   ├── child_0
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   └── member_1
    │       ├── child_0
    │       ├── dataset_0 [() object]
    │       └── member_0
    ├── dataset_0 [(3, 3) float64]
    ├── member_0
    │   ├── child_0
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [() object]
    │   │   └── member_0
    │   ├── child_1
    │   │   ├── child_0
    │   │   ├── dataset_0 [(3, 3) float64]
    │   │   └── member_0
    │   ├── dataset_0 [() object]
    │   ├── member_0
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   └── member_1
    │       ├── child_0
    │       ├── dataset_0 [(3, 3) float64]
    │       ├── dataset_1 [() object]
    │       ├── member_0
    │       └── member_1
    └── member_1
        ├── child_0
        │   ├── child_0
        │   ├── child_1
        │   ├── dataset_0 [(3, 3) float64]
        │   ├── dataset_1 [() object]
        │   ├── member_0
        │   └── member_1
        ├── dataset_0 [(3, 3) float64]
        ├── member_0
        │   ├── child_0
        │   ├── child_1
        │   ├── dataset_0 [(3, 3) float64]
        │   ├── dataset_1 [(3, 3) float64]
        │   ├── member_0
        │   └── member_1
        └── member_1
            ├── child_0
            ├── dataset_0 [() object]
            ├── dataset_1 [() object]
            ├── member_0
            └── member_1



```python
# access the data in /child_0/member_0/dataset_0
with h5.File('random.hdf5', 'r') as f: print(f['/child_0/member_0/dataset_0'][()])

#reassign a 2x2 matrix to the dataset
with h5.File('random.hdf5', 'r+') as f: 
    del f['/child_0/member_0/dataset_0']
    f.create_dataset('/child_0/member_0/dataset_0', data=np.random.rand(2,2))
    
# access the data in /child_0/member_0/dataset_0
with h5.File('random.hdf5', 'r') as f: print(f['/child_0/member_0/dataset_0'][()])

#create a new node after /child_0/child_0/child_0
with h5.File('random.hdf5', 'r+') as f: 
    # f['/child_0/child_0/child_0'].create_group('new_group/new_group/new_group')
    f['/child_0/child_0/child_0'].create_dataset('new_group/new_group/new_dataset2', data=np.random.rand(4,4))
```

    b'test_string'
    [[0.72553434 0.47512766]
     [0.43273966 0.09114334]]



```python
with h5.File('random.hdf5', 'r') as f: h5_tree(f)
```

    ├── child_0
    │   ├── child_0
    │   │   ├── child_0
    │   │   │   └── new_group
    │   │   │       └── new_group
    │   │   │           └── new_dataset2 [(4, 4) float64]
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   ├── member_0
    │   │   └── member_1
    │   ├── dataset_0 [() object]
    │   ├── dataset_1 [() object]
    │   └── member_0
    │       ├── child_0
    │       ├── child_1
    │       ├── dataset_0 [(2, 2) float64]
    │       └── member_0
    ├── child_1
    │   ├── child_0
    │   │   ├── child_0
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   ├── child_1
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [(3, 3) float64]
    │   │   └── member_0
    │   ├── dataset_0 [() object]
    │   ├── member_0
    │   │   ├── child_0
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   └── member_1
    │       ├── child_0
    │       ├── dataset_0 [() object]
    │       └── member_0
    ├── dataset_0 [(3, 3) float64]
    ├── member_0
    │   ├── child_0
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [() object]
    │   │   └── member_0
    │   ├── child_1
    │   │   ├── child_0
    │   │   ├── dataset_0 [(3, 3) float64]
    │   │   └── member_0
    │   ├── dataset_0 [() object]
    │   ├── member_0
    │   │   ├── child_0
    │   │   ├── child_1
    │   │   ├── dataset_0 [() object]
    │   │   ├── dataset_1 [(3, 3) float64]
    │   │   └── member_0
    │   └── member_1
    │       ├── child_0
    │       ├── dataset_0 [(3, 3) float64]
    │       ├── dataset_1 [() object]
    │       ├── member_0
    │       └── member_1
    └── member_1
        ├── child_0
        │   ├── child_0
        │   ├── child_1
        │   ├── dataset_0 [(3, 3) float64]
        │   ├── dataset_1 [() object]
        │   ├── member_0
        │   └── member_1
        ├── dataset_0 [(3, 3) float64]
        ├── member_0
        │   ├── child_0
        │   ├── child_1
        │   ├── dataset_0 [(3, 3) float64]
        │   ├── dataset_1 [(3, 3) float64]
        │   ├── member_0
        │   └── member_1
        └── member_1
            ├── child_0
            ├── dataset_0 [() object]
            ├── dataset_1 [() object]
            ├── member_0
            └── member_1

