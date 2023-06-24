# Optical-film-maker

An optical thin film design tool box.
Author: Jiang anqing
From: Yoshie Lab., IPS, Waseda Univ.

This repository is an edited version of original code provided for research.

## Setting up

`requirements.txt` is provided (but my requirements is from my root system, so may have unnecessary modules, sorry!)

## Running the code

To start the model, in root directory, run  
`python research/dqn.py | tee log/run_logs/log.txt`

Take note of the following:

- Run logs (policy and agent checkpoints) will be saved in `log/checkpoints` (maybe need to clear this directory before running, Tensorflow may sometimes error if this folder contains an existing checkpoint)
- Debug is turned on, and all output is outputted to `stdout` and `logs/run_logs/log.txt`. (on `research/dqn.py` line 37, set `debug=False` to turn off debugging)
- Even though all the steps are loggined in `run_logs/run_...txt`, we're not very sure if we are logging the correct data, so to avoid any loss of data all debugging output is stored.

## Changing initial state

A full list of the available materials is provided in `materials.txt` (use keys as names, e.g. `Ag_Johnson` or `Al_McPeak`.  
To modify the initial materials, change the list in `config/Zn.ini`.

- Change the materials list, while using the same indentation
- Change the `init_state` to have the correct number of elements (match with number of materials)
