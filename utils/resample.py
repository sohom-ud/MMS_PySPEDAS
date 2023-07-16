'''
Resample x to the resolution of y. (x and y must be pandas DataFrames)
'''

def resample(x, y):

    idx = y.index # Timestamps to resample to
    x = x[~x.index.duplicated()] # Check for any duplicate indices
    x = x.reindex(x.index.union(idx)).interpolate('index').reindex(idx)

    return x