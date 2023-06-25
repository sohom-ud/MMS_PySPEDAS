from __init__ import *

'''
Loads plasma velocity moments from FPI.
'''

def load_fpi_moms(trange, species="elc", probe="1", drate="brst", wipe=True):
    
    var_names = {
        "numberdensity": "N",
        "bulkv_gse": "v",
        "bulkv_err": "v_err",
        "bulkv_spintone_gse": "v_spin",
        "prestensor_gse": "Ptensor",
        "prestensor_err": "Ptensor_err" 
    }

    # scalar_vars = ['numberdensity']
    # vector_vars = ['bulkv_gse', 'bulkv_spintone_gse']
    # tensor_vars = ['prestensor_gse']

    data_dict = dict()

    dtype = "dis" if species == "ion" else "des"

    prefix = f"mms{probe}_{dtype}"

    varlist = dict()

    # Create list of variables
    for key, value in var_names.items():
        varlist[f'{prefix}_{key}_{drate}'] = f"{value}_{species}_{probe}"

    # Load FPI moment files
    try: 
        data = fpi(
            trange=trange,
            probe=probe,
            data_rate=drate,
            datatype=f"{dtype}-moms",
            center_measurement=True,
            varnames=list(varlist.keys()), 
            notplot=True
        )
    except:
        print("Data not found.")
        return
    
    for key, value in data.items():

        skey = varlist[key]

        dim = len(data[key]['y'].shape) - 1

        data_dict[skey] = dict()

        data_dict[skey]['Epoch'] = data[key]['x']
        data_dict[skey]['Values'] = data[key]['y']

        # if dim == 0:
        #     y = data[key]['y']
        #     cols = ['Epoch', skey]  #Scalar variable
        # elif dim == 1:
        #     y = data[key]['y']
        #     cols = ['Epoch', f'{skey}_x', f'{skey}_y', f'{skey}_z']
        # elif dim == 2:
        #     y = data[key]['y'].reshape(len(data[key]['y']), 9)
        #     cols = ['Epoch', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx', f'{skey}_xx']

        # x = data[key]['x']
        # data_dict[skey] = pd.DataFrame(data=np.column_stack([x, y]), columns=cols)
        # data_dict[skey].set_index('Epoch', inplace=True)
    
    if 'v' and 'v_spin' in var_names.values():

        data_dict[f'v_spincorr_{species}_{probe}'] = dict()
        data_dict[f'v_spincorr_{species}_{probe}']['Epoch'] = data_dict[f'v_{species}_{probe}']['Epoch']
        data_dict[f'v_spincorr_{species}_{probe}']['Values'] = data_dict[f'v_{species}_{probe}']['Values'] - data_dict[f'v_spin_{species}_{probe}']['Values']

        # v_corr = data_dict[f'v_{species}_{probe}'].values - data_dict[f'v_spin_{species}_{probe}'].values
        # v_corr_cols = ['Epoch', 'v_x', 'v_y', 'v_z']
        # data_dict[f'v_spincorr_{species}_{probe}'] = pd.DataFrame(data=np.column_stack([x, v_corr]), columns=v_corr_cols)
        # data_dict[f'v_spincorr_{species}_{probe}'].set_index('Epoch', inplace=True)
        
    return data_dict

'''
Loads magnetic field data from FGM.
'''

def load_fgm(trange, probe="1", drate="brst", wipe=True):

    var_names = [
        'Epoch', 
        'b_gse', 
        'r_gse'
    ]

    data_dict = dict()

    prefix = f"mms{probe}_fgm"
    suffix = f"{drate}_l2"

    # Create list of variables
    
    varlist = {f'{prefix}_{var}_{suffix}': f"{var}_{probe}" for var in var_names}

    # Load FGM data
    data = fgm(
        trange=trange, 
        probe=probe, 
        data_rate=drate,
        varnames=list(varlist.keys()),
        notplot=True
    )

    for key, value in data.items():

        skey = varlist[key]

        data_dict[skey] = dict()

        data_dict[skey]['Epoch'] = data[key]['x']
        data_dict[skey]['Values'] = data[key]['y']
        # dim = len(data[key]['y'].shape) - 1

        # if dim == 0:
        #     cols = ['Epoch', skey]  #Scalar variable
        # elif dim == 1:
        #     cols = ['Epoch', f'{skey}_x', f'{skey}_y', f'{skey}_z']

        # data_dict[skey] = pd.DataFrame(data=np.column_stack([data[key]['x'], data[key]['y']], columns=cols))
        # data_dict[skey].set_index('Epoch')

    return data_dict

'''
Clips data to specified time range
'''

def time_clip(data, trange):

    start_time = pd.Timestamp(trange[0]).timestamp()
    end_time = pd.Timestamp(trange[1]).timestamp()
   
    for key, value in data.items():

        # epoch = data[key].index
        epoch = data[key]['Epoch']

        cond = np.logical_and(epoch>=start_time, epoch<=end_time)

        data[key]['Epoch'] = data[key]['Epoch'][cond]
        data[key]['Values'] = data[key]['Values'][cond]

        # data[key] = data[key][cond]

'''
Write data to .h5 file
'''

def write_data(data, trange):

    start_time = pd.to_datetime(trange[0]).strftime('%Y%m%d_%H%M%S')
    end_time = pd.to_datetime(trange[1]).strftime('%Y%m%d_%H%M%S')

    fname = os.path.join(data_dir, f'{start_time}_{end_time}.h5')

    # if timeclip:
    #     data = time_clip(data, trange)

    with h5py.File(fname, 'a') as f:

        for key in data.keys():

            f.create_group(key)

            f.create_dataset(f"{key}/Epoch", data=data[key]['Epoch'])
            f.create_dataset(f"{key}/Values", data=data[key]['Values'])
            # data[key].to_hdf(fname, key=f'main/{key}')
            
            print(f"Written {key} to file.")

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

'''
Clip and interpolate data so that the measurements of all 4 s/c have the same timestamps
'''

def interpolate_r(data):
        
    ms = data[f'b_gse_1']['Epoch'][0]
    me = data[f'b_gse_1']['Epoch'][-1]

    dt = 1/128.0 # Time resolution of magnetic field

    # Find minimum start time and maximum end time
    for probe in [1, 2, 3, 4]:
        
        max_start_time = max(ms, data[f'b_gse_{probe}']['Epoch'][0])
        min_end_time = min(me, data[f'b_gse_{probe}']['Epoch'][-1])

    for probe in [1, 2, 3, 4]:

        t = data[f'r_gse_{probe}']['Epoch']
        r = data[f'r_gse_{probe}']['Values']

        df = pd.DataFrame(data=np.column_stack([t, r]))
        df.set_index(0, inplace=True)

        df = df.drop_duplicates()

        t = df.index
        r = df.values

        f = interp1d(t, r, axis=0, kind='quadratic', fill_value="extrapolate")

        tnew = np.arange(max_start_time, min_end_time, dt) 

        # Resampling positions to tnew

        data[f'r_gse_{probe}']['Epoch'] = tnew
        data[f'r_gse_{probe}']['Values']= f(tnew)

'''
Interpolate the magnetic field measurements from all 4 s/c to the same time range
'''

def interpolate_b(data):

    ms = data[f'b_gse_1']['Epoch'][0]
    me = data[f'b_gse_1']['Epoch'][-1]

    dt = 1/128.0 # Time resolution of magnetic field

    # Find minimum start time and maximum end time
    for probe in [1, 2, 3, 4]:
        
        max_start_time = max(ms, data[f'b_gse_{probe}']['Epoch'][0])
        min_end_time = min(me, data[f'b_gse_{probe}']['Epoch'][-1])

    for probe in [1, 2, 3, 4]:

        t = data[f'b_gse_{probe}']['Epoch']
        b = data[f'b_gse_{probe}']['Values']
        
        df = pd.DataFrame(data=np.column_stack([t, b]))
        df.set_index(0, inplace=True)

        df = df.drop_duplicates()

        t = df.index
        b = df.values

        f = interp1d(t, b, axis=0, kind='quadratic', fill_value="extrapolate")

        tnew = np.arange(max_start_time, min_end_time, dt) 

        data[f'b_gse_{probe}']['Epoch'] = tnew
        data[f'b_gse_{probe}']['Values'] = f(tnew)

def interpolate_v_n_P(data, species='ion'):
   
    ms = data[f'v_{species}_1']['Epoch'][0]
    me = data[f'v_{species}_1']['Epoch'][-1]

    dt = 0.150 if species =='ion' else 0.03 # Time resolution of moments in seconds

    # Find minimum start time and maximum end time
    for probe in [1, 2, 3, 4]:
        
        max_start_time = max(ms, data[f'v_{species}_{probe}']['Epoch'][0])
        min_end_time = min(me, data[f'v_{species}_{probe}']['Epoch'][-1])

    for var in ['v', 'v_spin', 'v_spincorr', 'N', 'Ptensor']:

        for probe in [1, 2, 3, 4]:

            t = data[f'{var}_{species}_{probe}']['Epoch']
            v = data[f'{var}_{species}_{probe}']['Values']
            
            if var == 'Ptensor':

                v = data[f'{var}_{species}_{probe}']['Values'].reshape(len(t), 9)

            df = pd.DataFrame(data=np.column_stack([t, v]))
            df.set_index(0, inplace=True)

            df = df.drop_duplicates()

            t = df.index
            v = df.values

            f = interp1d(t, v, axis=0, kind='quadratic', fill_value="extrapolate")

            tnew = np.arange(max_start_time, min_end_time, dt) 

            data[f'{var}_{species}_{probe}']['Epoch'] = tnew
            data[f'{var}_{species}_{probe}']['Values'] = f(tnew)


'''
Compute the reciprocal vectors of tetrahedron (required for estimation of gradients)
'''

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

def resample(x, y):

    '''
    Resample x to the resolution of y.
    Both x and y must be pandas DataFrames
    '''
    idx = y.index # Timestamps to resample to
    x = x[~x.index.duplicated()] # Check for any duplicate indices
    x = x.reindex(x.index.union(idx)).interpolate('index').reindex(idx)

    return x