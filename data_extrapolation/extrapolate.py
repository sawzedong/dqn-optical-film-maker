#!/usr/bin/env python

import yaml
import os
import pandas as pd

material_name = "SiO2"
page_name = "Rodriguez"
lower_limit = 300 #nm
upper_limit = 1500 #nm
step = 1 #nm

# NOTE: if using existing file, ensure lower_limit, upper_limit and step match the existing file

file_path = os.path.join("./data_extrapolation/data", f"{material_name}_{page_name}.yml")
data = ""

with open(file_path, "r") as stream:
    try:
        data = yaml.safe_load(stream)['DATA'][0]['data']
    except yaml.YAMLError as exc:
        print(exc)

data_items = [[float(k) for k in i.split(" ") if k != ""] for i in data.split("\n")][:-1]
wavelengths = [i[0] for i in data_items]
n = [i[1] for i in data_items]
k = [i[2] for i in data_items]

max_i = 0
for i in range(len(wavelengths)):
    if wavelengths[i] <= (lower_limit/1000) < wavelengths[i+1]:
        max_i = i+1
        break

new_data = []
dict_data = {}
counter = 0

for wl in range(lower_limit, upper_limit+1, step):
    counter += 1
    for i in range(max_i-1, len(wavelengths)):
        wl_micro = wl / 1000
        if wavelengths[i] <= wl_micro < wavelengths[i+1]:
            w_up = wl_micro - wavelengths[i] # weigh the upper value higher if the distance to the lower value is higher
            w_low = wavelengths[i+1] - wl_micro
            n_new = (n[i]*w_low + n[i+1]*w_up)/(w_up+w_low)
            k_new = (k[i]*w_low + k[i+1]*w_up)/(w_up+w_low)
            new_data.append([wl, n_new, k_new])
            dict_data[wl] = [n_new, k_new]
            max_i = i+1
df = pd.DataFrame(new_data, columns=['Wavelength (nm)', f'{material_name}_n', f'{material_name}_k'])

use_existing_csv = True
csv_filepath = "./data_extrapolation/data.csv"
if not use_existing_csv:
    df.to_csv(csv_filepath, index=False)
else:
    existing_df = pd.read_csv(csv_filepath)
    existing_data = existing_df.values.tolist()
    for i in range(len(existing_data)):
        existing_data[i].append(dict_data[existing_data[i][0]][0])
        existing_data[i].append(dict_data[existing_data[i][0]][1])
    column_names = list(existing_df.columns) + [f'{material_name}_n', f'{material_name}_k']
    df_new = pd.DataFrame(existing_data, columns=column_names)
    df_new.to_csv(csv_filepath, index=False)
    
