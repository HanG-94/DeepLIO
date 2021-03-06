import os
import sys
import time
import argparse
import glob
import threading
import multiprocessing
from multiprocessing import Pool
from pathlib import Path
import tqdm
import numpy as np
import pickle

dname = os.path.dirname(__file__)
module_dir = os.path.abspath("{}/deeplio".format(dname))
content_dir = os.path.abspath("{}/..".format(dname))
sys.path.append(dname)
sys.path.append(module_dir)
sys.path.append(content_dir)

from deeplio.common import utils
from deeplio.datasets import KittiRawData

def convert_oxts2bin(args):
    bar_pos = args[0]

    ds_data = args[1]
    base = ds_data[0]
    drive = ds_data[1]
    date = ds_data[2]

    print("Processing {}_{}".format(date, drive))
    dataset = KittiRawData(base, date, drive, lazy_load=False)
    # now saving the tranformed data as a pickle binary
    oxts_bin_path = os.path.join(dataset.data_path, "oxts", "data.pkl")
    with open(oxts_bin_path, 'wb') as f:
        pickle.dump(dataset.oxts, f)
    print('done!')

def convert(args):
    n_worker = len(args['path'])
    counters = list(range(n_worker))
    ds_data = []
    for path in args['path']:
        # we assume path has following structure:
        # /some/folder/KITTI/2011_10_03/2011_10_03_drive_0027_extract/oxts/data
        p = Path(path)
        parents = list(p.parents)
        base = str(parents[3].absolute())
        drive = parents[2].stem
        date = parents[1].stem.split('_')[-2]
        ds_data.append([base, date, drive])

    procs = Pool(processes=n_worker, initializer=tqdm.tqdm.set_lock, initargs=(tqdm.tqdm.get_lock(),))
    procs.map(convert_oxts2bin, zip(counters, ds_data))
    procs.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DeepLIO Training')

    # Device Option
    parser.add_argument('-p',  '--path', nargs="+", help='path or a list paths to velodyne text files', required=True)
    args = vars(parser.parse_args())
    convert(args)
    print("done!")





