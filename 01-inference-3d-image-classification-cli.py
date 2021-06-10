import os
import zipfile
import numpy as np
import tensorflow as tf
import logging
import time
from tensorflow import keras
from tensorflow.keras import layers

logging.basicConfig(level=logging.INFO)

#
# Load model from storage.
#
import requests
url = "https://koz.s3.amazonaws.com/models/3d_image_classification.h5"
model_file = '3d_image_classification.h5'

filename = os.path.join(os.getcwd(), model_file)
keras.utils.get_file(filename, url)

model = keras.models.load_model(filename)

#
# Load volume data from storage.
#
url = "https://koz.s3.amazonaws.com/data/ct-data.zip"
filename = os.path.join(os.getcwd(), "ct-data.zip")
keras.utils.get_file(filename, url)

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
    # payload format
    # payload = {"data": {"ndarray": X.tolist()} }
    #
    
    # 
    # Load the data set for prediction.
    #
    v = read_nifti_file(filename)

    # Local prediction.
    prediction = model.predict(np.expand_dims(v, axis=0))[0]
    logging.info(f'{filename} Local Prediction = {prediction[0]:.3f}')

    #
    # Prediction via REST.
    #
    url = 'http://mymodel-mygroup-ml-mon.2886795286-80-hazel05.environments.katacoda.com/api/v1.0/predictions'
    logging.info(f'Serializing and predicting volume {filename} via REST...')
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

