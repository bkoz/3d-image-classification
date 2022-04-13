#
# Make an ML model prediction via REST
#

import os
import zipfile
import numpy as np
import logging
import time
import urllib.request

logging.basicConfig(level=logging.INFO)

#
# Load volume data from storage.
#
url = "https://koz-models.s3.us-east-2.amazonaws.com/ct-data.zip"
filename = os.path.join(os.getcwd(), "ct-data.zip")
urllib.request.urlretrieve(url, filename)

# Unzip data in the newly created directory.
with zipfile.ZipFile("ct-data.zip", "r") as z_fp:
    z_fp.extractall("./")

import nibabel as nib
from scipy import ndimage

def read_nifti_file(filepath):
    """Read and load volume"""
    # Read file
    scan = nib.load(filepath)
    # Get raw data
    scan = scan.get_fdata()
    return scan

import requests

def predict(filename):
    #
    # REST payload format
    # payload = {"data": {"ndarray": X.tolist()} }
    #
    
    # 
    # Load the data set for prediction.
    #
    v = read_nifti_file(filename)

    #
    # Prediction via REST.
    #
    #
    # CHANGE hostname to reflect your cluster.
    #
    hostname = 'http://mymodel-mygroup-bk-models.apps.cluster-cghmd.cghmd.sandbox879.opentlc.com'
    url = f'{hostname}/api/v1.0/predictions'
    
    logging.info(f'Serializing and predicting volume {filename} via REST at URL: {url}')
    payload = {"data": {"ndarray": v.tolist()} }
    try:
        t0 = time.time()
        r = requests.post(url, json = payload, timeout = 20)
    except requests.exceptions.ConnectionError:
        logging.info(f'REST connection error!')
        return None
    
    logging.debug(f'response: {r}')
    j = r.json()['data']['ndarray'][0]
    logging.info(f'{filename} REST prediction = {j:.3f}, elapsed time = {time.time() - t0:.1f}s')

    pass

#
# Load a volume so default dimensions are known for interaction widgets.
#
global global_v
study = 0
filename = f'./data/volume{study}.nii.gz'
global_v = read_nifti_file(filename)

#
# Loop through the predictions.
#
for study in range(5):
        logging.debug(f'set_volume = {study}')
        if (study != None):
            filename = f'./data/volume{study}.nii.gz'
            logging.debug(f'Loading {filename}')
            filename = f'./data/volume{study}.nii.gz'
            v = read_nifti_file(filename)
            logging.debug(f'Calling slicer with {filename}, mean = {v.mean()}')
            predict(filename)

