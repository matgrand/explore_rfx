# Stuff I learned exploring the RFX tree
This will be either a short list or a long list:
- There are signals with no raw data, but values and timesteps are just 2 arrays
- most signals are built with a raw signal, timesteps are a formula from which the actual timestamps
  array is built. Values are also built with a formula from the raw signal.
- Build_Dim(Build_Window(0, 2749, -.33), * : * : .0004) means build a signal range with dt=0.0004,
  it will create a vector of times that has element 0 at -0.33, and took 0 samples before and 2749
  samples after that time. usually the first param is always 0 so that the signal starts at index 0,
  and the trigger coincides with the first sample.
  https://www.mdsplus.org/index.php/Documentation:dt_dimension
- In the paths to the nodes: '.' means its a child, and ':' means its a member of the previous node.