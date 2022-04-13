import tensorflow
from tensorflow import keras
from keras.models import load_model
import os
from os import environ
import requests
import keras
import numpy as np


class MyModel:
    def __init__(self):
        pass

    def predict(self, X, features_names=None):
        print(f'predict() called, input X.shape = {X.shape}.')
        print(self._model.summary())
        x = np.zeros((128, 128, 64, 1))
        p = np.array([0.66, 0.33])
        #
        # For testing, call the predictor with input x vs. X so the dimensions match.
        #
        self._prediction = self._model.predict(np.expand_dims(X, axis=0))[0]
        print(f'Prediction = {self._prediction}')
        print(f'Length of prediction = {len(self._prediction)}')
        return np.array(self._prediction)

    def load(self):
        #
        # Load model from an http server.
        #
        url = "https://koz-models.s3.us-east-2.amazonaws.com/3d_image_classification.h5"
        home = os.environ['HOME']
        model_file = f'{home}/3d_image_classification.h5'
        print(f'********************* tensorflow version: {tensorflow.__version__} *************************')
        print(f'*** Downloading model to {model_file}')
        print(f'********************* tensorflow version: {tensorflow.__version__} *************************')

        receive = requests.get(url)

        with open(model_file,'wb') as f:
            f.write(receive.content)

        self._model = keras.models.load_model(model_file)

    def tags(self):
        return {"Abnormal": str(self._prediction[0] > 0.5)}
    
    def health_status(self):
        response = self.predict(np.array([1, 2]), ["f1", "f2"])
        print(f'health_status() called.')
        assert len(response) == 1, "health check returning bad predictions" # or some other simple validation
        return response
