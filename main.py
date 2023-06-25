from __init__ import *
from __methods import *
from compute_jcurl import *

if __name__ == "__main__":

    trange = ['2017-12-26/06:12:43', '2017-12-26/06:52:23']
    # trange = ['2023-02-02/21:02:33', '2023-02-02/21:05:33']

    data = dict()
    
    for probe in [1, 2, 3, 4]:

        fgm_data = {}
        fpi_data_ions = {}
        fpi_data_electrons = {}

        try:
            fgm_data = load_fgm(trange, probe=probe, wipe=False)
            data = dict(data, **fgm_data)
            # fgm_data = time_clip(fgm_data, trange)
        except:
            print(f"No magnetic field data found for MMS{probe}.")

        try:
            fpi_data_ions = load_fpi_moms(trange, species='ion', probe=probe, wipe=False)
            data = dict(data, **fpi_data_ions)
        except:
            print(f"No ion moments found for MMS{probe}.")
        
        try:
            fpi_data_electrons = load_fpi_moms(trange, species='elc', probe=probe, wipe=False)
            data = dict(data, **fpi_data_electrons)
        except:
            print(f"No electron moments found for MMS{probe}.")

        # data = dict(data, **fgm_data)

    k = compute_k(data) 

    interpolate_v_n_P(data, 'ion')
    interpolate_v_n_P(data, 'elc')

    fgm_data = time_clip(fgm_data, trange)
    # k = time_clip(k, trange)

    data = dict(data, **k)    
    
    time_clip(data, trange)

    write_data(data, trange)