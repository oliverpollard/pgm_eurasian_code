import numpy as np
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm
import xarray as xr
import rioxarray
import sys

ens_idx = int(sys.argv[1])

from shearpy import make_shear_stress_map

shear_stress_map_name = "ely_victor_eurasia"
shear_stress_map_file = "/nfs/annie/cm15ogp/data/shear_stress/eurasia_expanded/regions.shp"

dx = 5000
dy = 5000
x_min = -1265453.0
x_max = 4159547.0
y_min = -4722734.8
y_max = 1352265.2
grid_x = np.arange(x_min, x_max+dx, dx)
grid_y = np.arange(y_min, y_max+dy, dy)

grid_crs = '+ellps=WGS84 +proj=laea +lon_0=0.0 +lat_0=90 +x_0=0.0 +y_0=0.0 +no_defs'

num_margins = 1

cols = [
    'g_pgm_ice_streams_ice_stream',
    'g_sediment_marine_sediment',
    'g_sediment_onshore_sediment',
    'g_sediment_bedrock',
    'p_ice_stream_interior_dist',
    'p_cold_ice_shear_stress',
    'p_cold_ice_interior_dist',
    'p_hybrid_ice_stream_shear_stress',
    'p_hybrid_ice_stream_dist'
]
param_vals = pd.read_csv("sample.csv", index_col=0)
param_vals = param_vals[cols]

shear_stress_parameters_const = {
    "m_base_map_name": shear_stress_map_name,
    "m_base_map_file": shear_stress_map_file,
    "m_gauss_blur": 1,
    "m_base_value": 5000,
    "m_combine_pattern": "((g_sediment | (g_pgm_ice_streams * p_ice_stream)) | p_hybrid_ice_stream) | p_cold_ice",
    "g_layers": ["sediment", "pgm_ice_streams"],
    "p_processes": ["ice_stream", "cold_ice", "hybrid_ice_stream"],
}

values = param_vals.iloc[ens_idx]
margins_dir = f"margins/{ens_idx}/"

margin_filename = str(Path(margins_dir) / f"0.shp")
shear_stress_parameters_margins = {
    "p_margin_name": f"interp_{ens_idx}",
    "p_margin_time": 0,
    "p_margin_file": margin_filename,
}
shearstress_path = Path(f"shearstress/{ens_idx}/")
shearstress_path.mkdir(exist_ok=True, parents=True)
shearstress_file = shearstress_path / f"0.nc"

shear_stress_parameters_var = values.to_dict()
shear_stress_parameters = {
    **shear_stress_parameters_const, 
    **shear_stress_parameters_var, 
    **shear_stress_parameters_margins,
}

make_shear_stress_map(
    grid_x = grid_x, 
    grid_y = grid_y, 
    grid_crs = grid_crs, 
    parameters = shear_stress_parameters,
    save=str(shearstress_file)
)