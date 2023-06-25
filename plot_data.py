from __init__ import *
from __methods import *

def plot(fname, vars):

    l = len(vars)

    f = h5py.File(fname, 'r')

    fig, axs = plt.subplots(l, 1, sharex=True)
    
    for i in range(len(vars)):

        epoch = f[vars[i]]['Epoch']
        values = f[vars[i]]['Values']
        epoch = list(map(lambda x: pd.Timestamp.utcfromtimestamp(x), epoch))
        axs[i].plot(epoch, values)
        axs[i].set_ylabel(vars[i])

    plt.xlabel('Datetime(UTC)')

    f.close()
    
    return fig, axs
