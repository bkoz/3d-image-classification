# Visualization and Classification of Pneumonia using 3D CT Images 

![Slicer](images/slicer.jpg "Slicer")

## Introduction

This repository contains a simple machine learning workflow consisting of
data ingestion and preparation, model training, serving and monitoring. It 
represents how computer-aided diagnosis can be used for the prediction 
of pneumonia from a collection (a volume) of CT images.

It is based on work by [Hasib Zunair.](https://keras.io/examples/vision/3D_image_classification/)

### Technologies Used
- Openshift
- OpenDataHub
- Jupyter Notebooks with iPyWidgets
- Numpy
- Tensorflow
- Python requests library
- Seldon Core
- Prometheus
- Grafana

### Relevant Files and Directories
```
├── 01-inference-3d-image-classification-cli.py        Python script forinferencing
├── 01-inference-3d-image-classification.ipynb         Visualization and inferencing
├── 02-training-3d-image-classification.ipynb          Notebook script for training
├── 02-training-3d-image-classification.py             Python script for training
├── 3d_image_classification.h5                         Trained model artifact
├── Dockerfile                                         For s2i builds
├── MyModel.py                                         Seldon Model Server Code
├── ct-data.zip                                        Validation data for inferencing
├── requirements-notebook.txt
├── requirements.txt
└── resources                                          Kubernetes Objects
    ├── 06-seldon-mymodel-servicemonitor.yaml
    ├── 07-mymodel-seldon-deploy-from-quay.yaml
    └── grafana-dashboards
        ├── NVIDIA-DCGM-dashboard.json                 GPU Metrics
        └── seldon-dashboard.json                      Model Server Metrics
```

## Tested Environment
### OpenDataHub (ODH) v1.3 for JupyterHub support
### Openshift Container Platform (OCP) v4.10.26

## Model Serving Workflow
![Demo Workflow](images/demo-workflow.png "Workflow")

## Model Development and Training Workflow

Train a 17-layer, Convolutional Neural Network to predict the presence of COVID-19 related pneumonia from 3D CT imagery.

## Model Card
![Model card](images/model-card.png "Model")

- (200) COVID-19 related 3D CT image studies 
- Each study contains 36-54 slices of 512x512 pixels (voxels) each.
- Total size is ~2GB  (compressed)
- ~20 minutes to preprocess and train on an NVIDIA Tesla T4 GPU
- ML framework: Keras/Tensorflow  

[Data Source: Chest CT Scans with COVID-19 Related Findings](https://www.medrxiv.org/content/10.1101/2020.05.20.20100362v1).

# Setup and Configuration

### Openshift
#### Model Server side 

0) Change to the `resources` directory.
```
cd 3d-image-classification/resources
```

1) Create a project called `ml-mon`
```
oc new-project ml-mon
```

2) Using the Openshift console UI, install an instance of the following community operators from OperatorHub into the `ml-mon` namespace.

- OpenDataHub
  - JupyterHub, S3, ODH Dashboard
- Prometheus
- Grafana

Seldon
- Install the Seldon Core operator into all namespaces in the cluster (default).

3) Create an instance of Prometheus and Grafana in the `ml-mon` namespace.

Expected Output
```
oc get pods -n ml-mon -w
```
```
NAME                                   READY   STATUS    RESTARTS   AGE
$ oc get pods -n ml-mon             

NAME                                                   READY   STATUS    RESTARTS   AGE
grafana-deployment-8fbf7c944-7895m                     1/1     Running   0          5h35m
grafana-operator-controller-manager-6ff698d9fc-xvk28   2/2     Running   0          5h35m
prometheus-example-0                                   2/2     Running   0          5h35m
prometheus-operator-7b9ccd45c6-7v8td                   1/1     Running   0          5h35m
```

Create routes for Prometheus and Grafana.
```
oc expose svc prometheus-operated
oc expose svc grafana-service
```

Obtain the Grafana admin credentials to login to the Grafana console.
```
oc get secrets grafana-admin-credentials -o=jsonpath='{@.data.GF_SECURITY_ADMIN_USER}' | base64 --decode

admin

oc get secrets grafana-admin-credentials -o=jsonpath='{@.data.GF_SECURITY_ADMIN_PASSWORD}' | base64 --decode

ABcdRqpfdsEfpg==
```

![Operators](images/operators.jpg "Operators")

4) Create a Prometheus Service Monitor
```
oc create -f 06-seldon-mymodel-servicemonitor.yaml

servicemonitor.monitoring.coreos.com/mymodel-mygroup created
```
5) Login to the Grafana console. The username and password can be obtained from the
`grafana-admin-credentials` secret.
6) Within Grafana, configure a Prometheus data source called `prometheus` with a URL of `prometheus-operated.ml-mon:9090`

7) Import the Seldon dashboard from the `resources/seldon-dashboard.json` file.

7) Deploy the Seldon model server and wait for the classifier pod to become ready. Two services should be created by the Seldon deployer.
```
oc create -f 07-mymodel-seldon-deploy-from-quay.yaml

seldondeployment.machinelearning.seldon.io/mymodel created
```

```
oc get pods
```
```
NAME                                            READY   STATUS    RESTARTS   AGE
mymodel-mygroup-0-classifier-57647887d9-98qqb   2/2     Running   0          118s
```
```
oc get services
```
```
NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
mymodel-mygroup              ClusterIP   10.217.5.143   <none>        8000/TCP,5001/TCP   20s
mymodel-mygroup-classifier   ClusterIP   10.217.4.127   <none>        9000/TCP            2m4s
```

8) Create a route for the Seldon model server.
```
oc expose svc mymodel-mygroup
```

Curl the prometheus endpoint and confirm it is able to scrape metrics from the classifier pod.
```
curl -X GET $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/prometheus
```
```
...
promhttp_metric_handler_requests_total{code="200"} 5
```

## OpenDataHub and Jupyter Client Configuration

Jupyter Notebook dependencies

```  
pip install tensorflow jupyterlab ipywidgets scipy
```

- Login to OpenDataHub
- Start the JupyterHub server and choose the `Standard Data Science` notebook image.
- Clone this github repo
- Run the `01-inference-3d-image-classification` notebook.
- Find the notebook cell with `predict` function and modify the `url` variable to point to the route that was created.
  - `echo $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/api/v1.0/predictions`
- Run the notebook and select a study to make a few predictions to trigger Seldon activity.

Within 30 seconds or so there should be activity on the Seldon Grafana Dashboard.

Optionally, [configure Grafana to watch Openshift's built-in Prometheus Data Source](https://www.redhat.com/en/blog/custom-grafana-dashboards-red-hat-openshift-container-platform-4)
so a GPU dashboard can be created. This data source will scrape metrics from the NVIDA
DCGM exporter.

Grant the Grafana service account name the `cluster-reader` role so it can use
Openshift's Prometheus in the `openshift-monitoring` namespace.

```
oc adm policy add-cluster-role-to-user cluster-monitoring-view -z grafana-service-account -n ml-mon
```

Get the Prometheus token.
```
oc serviceaccounts get-token prometheus-k8s -n openshift-monitoring
```

Add this token to the example Grafana data source yaml.
```
httpHeaderValue1: 'Bearer ${BEARER_TOKEN}'
```

Create the data source object.
```
oc apply -f 03-prometheus-grafanadatasource.yaml
```

Import the Seldon and [GPU](https://grafana.com/grafana/dashboards/12239-nvidia-dcgm-exporter-dashboard/) dashboards from the included json files.

Open The Prometheus and Grafana Dashboards to visualize the API activity.

![Grafana](images/grafana.jpg "Grafana")

### Trouble Shooting

### How to confirm that Proetheus is scraping metrics from Seldon.

```
curl -X GET $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/prometheus
```
```
seldon_api_executor_server_requests_seconds_sum{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions"} 4.714845908
seldon_api_executor_server_requests_seconds_count{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions"} 5
```

```
$ oc create -f resources/07-mymodel-seldon-deploy-from-quay.yaml
Error from server (InternalError): error when creating "resources/07-mymodel-seldon-deploy-from-quay.yaml": Internal error occurred: failed calling webhook "v1.vseldondeployment.kb.io": Post "https://seldon-webhook-service.odh.svc:443/validate-machinelearning-seldon-io-v1-seldondeployment?timeout=30s": service "seldon-webhook-service" not found
```

This can happen after ODH has been re-installed into a different project. To fix it delete the old webhook.

```
oc get MutatingWebhookConfiguration,ValidatingWebhookConfiguration -A

oc delete validatingwebhookconfiguration.admissionregistration.k8s.io/seldon-validating-webhook-configuration-odh
```

## Developer Notes (Optional)

#### Building the Seldon deployer container image using OpenShift's s2i workflow.

#### Create and start a new build.

```
cd 3d-image-classification

oc new-build --strategy docker --docker-image registry.redhat.io/ubi8/python-36 --name mymodel -l app=mymodel --binary

oc start-build mymodel --from-dir=. --follow
```
```
oc get is

NAME      IMAGE REPOSITORY                                                     TAGS     UPDATED
mymodel   image-registry.openshift-image-registry.svc:5000/bk-models/mymodel   latest   7 seconds ago
```

Edit `mymodel-seldon-deploy.yaml` to confirm that the image location matches what the image stream reports. Then deploy the model server and wait for the pod to become ready.

```
oc apply -f resources/mymodel-seldon-deploy.yaml
```
```
oc get pods

NAME                                            READY   STATUS              RESTARTS   AGE
mymodel-mygroup-0-classifier-7c6b44569c-qmzk6   2/2     Running             0          61s
```

Expose the service
```
oc expose svc <svc-name>
```

To trigger a redeploy after a new build. This does not always work so the pod may have to be deleted.

```
oc patch deployment <deployment-name> -p "{\"spec\": {\"template\": {\"metadata\": { \"labels\": {  \"redeploy\": \"$(date +%s)\"}}}}}"
```
