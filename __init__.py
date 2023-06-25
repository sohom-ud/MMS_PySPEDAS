import os
import h5py
from pyspedas.mms import fpi, fgm
import astropy.units as u
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

data_dir = os.path.join(os.getcwd(), 'Data')
