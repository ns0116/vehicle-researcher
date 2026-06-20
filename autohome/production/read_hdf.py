import pandas as pd
from pathlib import Path

hdf_filename = Path(__file__).parent.parent / "all_series_car_specs.h5"
df = pd.read_hdf(hdf_filename, 'car_specs')
print(df.head())