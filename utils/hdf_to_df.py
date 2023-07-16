'''
Converts .h5 files to pandas DataFrames
'''

import h5py
import numpy as np
import pandas as pd

def hdf_to_df(fname, vars="all"):

    data = h5py.File(fname, 'r')

    df_dict = dict()

    if vars=="all":

        varlist = list(data.keys())

    else:

        varlist = vars

    for key in varlist:

        x = data[key]['Epoch'][...]
        
        y = data[key]['Values'][...]
        colnum = y.shape[1]

        if colnum == 1:
            cols = ['Epoch', 'val']  #Scalar variable
        elif colnum == 3:
            cols = ['Epoch', 'x', 'y', 'z']
        elif colnum == 4:
            cols = ['Epoch', 'x', 'y', 'z', 'mag']
        elif colnum == 9:
            y = data[key]['Values'][...].reshape(len(x), 9)
            cols = ['Epoch', 'xx', 'xy', 'xz', 'yx', 'yy', 'yz', 'zx', 'zy', 'zz']

        df_dict[key] = pd.DataFrame(data=np.column_stack([x, y]), columns=cols)
        df_dict[key]['Epoch'] = list(map(lambda x: pd.Timestamp.utcfromtimestamp(x), df_dict[key]['Epoch']))
        df_dict[key].set_index('Epoch', inplace=True)
        
    data.close()

    return df_dict        
