import numpy as np
import pandas as pd

from src.utils.compute_k import compute_k
from src.utils.interpolate_b import interpolate_b

mu0 = 4 * np.pi * 1e-7

def compute_jcurl(data):

    k = compute_k(data)
    b = dict()
    
    j = 0.0

    b_interp = interpolate_b(data)

    L = len(k[1]['Values'])

    for probe in [1, 2, 3, 4]:

        k[probe] = np.array(k[probe]['Values']).reshape(L, 3)
        b[probe] = b_interp[probe]['Values'][:, :3]
    
        j += np.cross(k[probe], b[probe])

    j = (j * 1e-12 / mu0)/1e-9

    j_df = pd.DataFrame(data=j, columns=['jx', 'jy', 'jz'])
    j_df.index = list(map(lambda x: pd.Timestamp.utcfromtimestamp(x), b_interp[1]['Epoch']))

    return j_df
