#
# Make an ML model prediction via local model file.
#

import os
import zipfile
import numpy as np
import logging
import time
import urllib.request
import tensorflow as tf

logging.basicConfig(level=logging.INFO)

#
# Load volume data from storage.
#
url = "https://koz.s3.amazonaws.com/data/ct-data.zip"
filename = os.path.join(os.getcwd(), "ct-data.zip")
logging.info(f'Loading {url}')
urllib.request.urlretrieve(url, filename)
logging.info(f'Loaded {url}')

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

def predict_local(filename):
    #
    # REST payload format
    # payload = {"data": {"ndarray": X.tolist()} }
    #
    
    # 
    # Load the data set for prediction.
    #
    v = read_nifti_file(filename)

    model = tf.keras.models.load_model("3d_image_classification/1")
    prediction = model.predict(np.expand_dims(v, axis=0))[0]
    logging.info(f'{filename} Local Prediction = {prediction[0]:.3f}')

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
            predict_local(filename)

