from __init__ import *
from __methods import *

# Computes the Pi tensor from .h5 file

def compute_gradv(fname, species='ion'):

    varlist = [f'v_spincorr_{species}_{probe}' for probe in [1, 2, 3, 4]] + [f'k_{probe}' for probe in [1, 2, 3, 4]]

    df_dict = hdf_to_df(fname, vars=varlist)

    k = dict()
    v = dict()

    for probe in [1, 2, 3, 4]:

        # Resample the reciprocal vectors to the resolution of the species moments
        
        k[probe] = resample(df_dict[f'k_{probe}'], df_dict[f'v_spincorr_{species}_{probe}'])

        v[probe] = df_dict[f'v_spincorr_{species}_{probe}']
        
    gradv_df = pd.DataFrame()
    gradv_df.index = k[1].index

    for comp1 in ['x', 'y', 'z']:

        for comp2 in ['x', 'y', 'z']:

            gradv_df[f'd{comp1}v{comp2}'] = 0.0

            for probe in [1, 2, 3, 4]:

                gradv_df[f'd{comp1}v{comp2}'] += k[probe][comp1] * v[probe][comp2]

    # gradv_df.index = k[1].index

    return gradv_df

def compute_avg_P(fname, species='ion'):

    varlist = [f'Ptensor_{species}_{probe}' for probe in [1, 2, 3, 4]]

    df_dict = hdf_to_df(fname, vars=varlist)

    P = dict()

    Pavg_df = pd.DataFrame()
    Pavg_df.index = df_dict[f'Ptensor_{species}_1'].index

    for probe in [1, 2, 3, 4]:

        P[probe] = df_dict[f'Ptensor_{species}_{probe}']

    Pavg_df = (P[1] + P[2] + P[3] + P[4])/4.0

    return Pavg_df

def compute_p(fname, species='ion'):

    Pavg = compute_avg_P(fname, species)

    p = (Pavg['xx'] + Pavg['yy'] + Pavg['zz'])/3.0

    return p

def compute_theta(fname, species='ion'):

    gradv_df = compute_gradv(fname, species)

    theta = (gradv_df['dxvx'] + gradv_df['dyvy'] + gradv_df['dzvz'])

    return theta

def compute_ptheta(fname, species='ion'):

    p = compute_p(fname, species)
    theta = compute_theta(fname, species)

    ptheta = pd.DataFrame()

    ptheta.index = p.index

    ptheta[f'ptheta_{species}'] = p.values * theta.values

    return ptheta

def compute_Dij(fname, species='ion'):

    gradv_df = compute_gradv(fname, species)
    theta = compute_theta(fname, species)

    D = pd.DataFrame()

    D.index = gradv_df.index

    for comp1 in ['x', 'y', 'z']:

        for comp2 in ['x', 'y', 'z']:

            D[f'{comp1}{comp2}'] = (gradv_df[f'd{comp1}v{comp2}'] + gradv_df[f'd{comp2}v{comp1}'])/2.0 - (theta * (comp1 == comp2))/3.0

    return D

def compute_Pi_ij(fname, species='ion'):

    Pavg = compute_avg_P(fname, species)
    p = compute_p(fname, species)

    Pi_ij = pd.DataFrame()
    Pi_ij.index = Pavg.index

    for comp1 in ['x', 'y', 'z']:
        
        for comp2 in ['x', 'y', 'z']:

            Pi_ij[f'{comp1}{comp2}'] = Pavg[f'{comp1}{comp2}'] - (p * (comp1 == comp2))

    return Pi_ij

def compute_PiD(fname, species='ion'):
    '''
    Returns value of Pi-D without the negative sign included.
    '''
    Pi = compute_Pi_ij(fname, species)
    D = compute_Dij(fname, species)

    PiD = pd.DataFrame()

    PiD.index = Pi.index
    PiD[f'PiD_{species}'] = 0.0

    for comp1 in ['x', 'y', 'z']:

        for comp2 in ['x', 'y', 'z']:

            PiD[f'PiD_{species}'] += Pi[f'{comp1}{comp2}'] * D[f'{comp1}{comp2}']

    return PiD

def compute_PS(fname, species='ion'):
    '''
    Returns value of PS without negative sign included.
    '''
    PiD = compute_PiD(fname, species)
    ptheta = compute_ptheta(fname, species)

    PS = pd.DataFrame()

    PS.index = PiD.index

    PS[f'PS_{species}'] = PiD.values + ptheta.values

    return PS