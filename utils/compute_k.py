'''
Compute the reciprocal vectors of MMS tetrahedron (required for estimation of gradients)
'''
import numpy as np
from .interpolate_r import interpolate_r

__all__ = ['compute_k']

def compute_k(data):

    k = dict()
    
    probe_list = [1, 2, 3, 4]

    interpolate_r(data)

    for num in probe_list:
        
        perm_list = [probe_list[(num + i) % 4] for i in probe_list]
    
        r1 = data[f'r_gse_{perm_list[0]}']['Values'][:, :3]
        r2 = data[f'r_gse_{perm_list[1]}']['Values'][:, :3]
        r3 = data[f'r_gse_{perm_list[2]}']['Values'][:, :3]
        r4 = data[f'r_gse_{perm_list[3]}']['Values'][:, :3]

        r12 = r2 - r1
        r13 = r3 - r1
        r14 = r4 - r1
        
        numerator = np.cross(r12, r13)
        denominator = (r14 * numerator).sum(axis=1)

        k[f'k_{num}'] = dict()

        k[f'k_{num}']['Epoch'] = data['r_gse_1']['Epoch']

        k[f'k_{num}']['Values'] = [numerator[i]/denominator[i] for i in range(len(r1))]
        k[f'k_{num}']['Values'] = np.array(k[f'k_{num}']['Values']).reshape(len(r1), 3)

    return k