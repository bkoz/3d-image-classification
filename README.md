# Classification of 3D Medical images 

## A basic data science demo using OpenDataHub and OpenShift Container Platform

Based on work by [Hasib Zunair](https://keras.io/examples/vision/3D_image_classification/)

### This is work in progress so the following documentation will not work.

### Steps

#### Server side configuration

1) Create the project
```
oc create -f 01-namespace.yaml   
oc project ml-mon
```

2) Create the ODH operator
```
oc create -f 02-odh-operator-subscription.yaml

oc get pods -n openshift-operators

NAME                                   READY   STATUS    RESTARTS   AGE
opendatahub-operator-5b6cb986d-48zxr   1/1     Running   0          3m22s
```

3) Create the ODH kfdef and wait for the pods to run.
```
oc create -f 03-opendatahub-kfdef-seldon-prometheus-grafana.yaml

oc get pods

grafana-deployment-5f6949bc8-ww97f              1/1     Running   0          7m10s
grafana-operator-cd65d6644-79mhv                1/1     Running   0          7m39s
odh-dashboard-764cbcb544-n8ff6                  1/1     Running   0          16m
odh-dashboard-764cbcb544-qfhkk                  1/1     Running   0          16m
prometheus-odh-monitoring-0                     2/2     Running   1          3m12s
prometheus-odh-monitoring-1                     2/2     Running   1          3m11s
prometheus-operator-578ccd6c45-dmfbg            1/1     Running   0          3m21s
seldon-controller-manager-6d5d5d4d8-9pfhx       1/1     Running   0          7m37s
```

4, 5 ,6) Configure Prometheus and Grafana 
```
oc create -f 04-grafana-prometheus-datasource.yaml             
oc create -f 05-prediction-analytics-seldon-core-1.2.2.yaml
oc create -f 06-seldon-mymodel-servicemonitor.yaml
```

7) Create and wait for the classifier pods to become ready before creating the route in the next step. This is important
because (2) services are created by the Seldon deployer.

```
oc create -f 07-mymodel-seldon-deploy-from-quay.yaml
```

```
oc get pods

$ oc get pods

NAME                                            READY   STATUS    RESTARTS   AGE
mymodel-mygroup-0-classifier-57647887d9-98qqb   2/2     Running   0          118s

oc get svc

NAME                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
mymodel-mygroup              ClusterIP   10.217.5.143   <none>        8000/TCP,5001/TCP   20s
mymodel-mygroup-classifier   ClusterIP   10.217.4.127   <none>        9000/TCP            2m4s
```

8) Create the route.
```
oc create -f 08-mymodel-route.yaml
```

Curl the prometheus endpoint and confirm it is able to scrape metrics from the classifier pod.

```
curl -X GET $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/prometheus

promhttp_metric_handler_requests_total{code="200"} 34
```

Make a few predictions to trigger Seldon activity, wait 30 seconds then try the same curl as above. There should be some
Seldon entries now.

```
curl -X GET $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/prometheus

seldon_api_executor_server_requests_seconds_sum{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions"} 4.714845908
seldon_api_executor_server_requests_seconds_count{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions"} 5
```

Connect to Prometheus and query for seldon entries. If they appear then Grafana should pick up the activity.

```
$ curl <classifier-route>/prometheus

seldon_api_executor_server_requests_seconds_bucket{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions",le="0.005"} 0
```

Install the ODH operator (v.1.0.10)

Using the CLI:

```
oc apply -f resources/02-odh-operator-sub.yaml
```

Wait for the operator pod to deploy.

Create a project called `ml-mon` then create an OpenDataHub `kfdef`.

Wait for the OpenDataHub, Jupyter, Seldon, Grafana and Prometheus pods to deploy.

```
oc new-project ml-mon
oc apply -f resources/03-opendatahub-kfdef-seldon-prometheus-grafana.yaml
```

Wait for the operators and pods to deploy. This could take 8-10 minutes.

Grafana v3.10.0
Prometheus v0.37.0
Seldon v.1.2.1

```
grafana-deployment-5f6949bc8-ww97f              1/1     Running   0          7m10s
grafana-operator-cd65d6644-79mhv                1/1     Running   0          7m39s
odh-dashboard-764cbcb544-n8ff6                  1/1     Running   0          16m
odh-dashboard-764cbcb544-qfhkk                  1/1     Running   0          16m
prometheus-odh-monitoring-0                     2/2     Running   1          3m12s
prometheus-odh-monitoring-1                     2/2     Running   1          3m11s
prometheus-operator-578ccd6c45-dmfbg            1/1     Running   0          3m21s
seldon-controller-manager-6d5d5d4d8-9pfhx       1/1     Running   0          7m37s
```

```
oc apply -f grafana-prometheus-datasource.yaml
oc apply -f resources/grafana-prometheus-datasource.yaml
oc apply -f resources/prediction-analytics-seldon-core-1.2.2.yaml 
```

#### Create and start a new build.

```
oc new-build --strategy docker --docker-image registry.redhat.io/ubi8/python-36 --name mymodel -l app=mymodel --binary

oc start-build mymodel --from-dir=. --follow

```

Edit `mymodel-seldon-deploy.yaml` to match the environment and deploy.

```
oc apply -f resources/mymodel-seldon-deploy.yaml

oc expose svc <svc-name>
```

### Deploy with seldon using OpenShift s2i

Deploy a custom image using OpenShift s2i and Seldon. 
Based on [Brian's blog post](https://www.openshift.com/blog/serving-machine-learning-models-on-openshift-part-1). 
Also read this [medium article](https://towardsdatascience.com/to-serve-man-60246a82d953) 
by Alexander Sack that is explained well. 
[Additional](https://docs.primehub.io/docs/model-deployment-tutorial-package-image) info.

#### Deploy the Seldon model service.

```
oc apply -f resources/mymodel-seldon-deploy.yaml 
oc apply -f resources/seldon-mymodel-servicemonitor.yaml
```

To trigger a redeploy after a new build. This does not always work so the pod may have to be deleted.

```
oc patch deployment <deployment-name> -p "{\"spec\": {\"template\": {\"metadata\": { \"labels\": {  \"redeploy\": \"$(date +%s)\"}}}}}"
```

Test the prometheus endpoint.

```
curl -X GET $(oc get route detection-redhat -o jsonpath='{.spec.host}')/prometheus
```

### Prometheus and Grafana configuration.

Create a Prometheus data source.
```
oc apply -f resources/grafana-prometheus-datasource.yaml
```

Create a Grafana dashboard.
```
oc apply -f resources/prediction-analytics-seldon-core-1.2.2.yaml
```

Create a service monitor.
```
oc apply -f resources/seldon-service-monitor.yml
```

Testing

```
curl -X POST $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/api/v1.0/predictions -H 'Content-Type: application/json' -d '{ "data": { "ndarray": [[5.1, 3.5, 1.4, 0.2]] } }'

curl -X GET $(oc get route mymodel-mygroup -o jsonpath='{.spec.host}')/prometheus
```

Deploy outside of OpenShift directly from a Python environment.

```
seldon-core-microservice MyModel REST --service-type MODEL

curl -X POST -H 'Content-Type: application/json' -d '{"data": { "ndarray": [[1,2,3,4]]}}' http://localhost:5000/api/v1.0/predictions
```
#### Server Setup

The following pods should be running:

```
$ oc get pods

grafana-deployment-5f6949bc8-ww97f              1/1     Running   0          7m10s
grafana-operator-cd65d6644-79mhv                1/1     Running   0          7m39s
mymodel-mygroup-0-classifier-57647887d9-78lmg   2/2     Running   0          114s
odh-dashboard-764cbcb544-n8ff6                  1/1     Running   0          16m
odh-dashboard-764cbcb544-qfhkk                  1/1     Running   0          16m
prometheus-odh-monitoring-0                     2/2     Running   1          3m12s
prometheus-odh-monitoring-1                     2/2     Running   1          3m11s
prometheus-operator-578ccd6c45-dmfbg            1/1     Running   0          3m21s
seldon-controller-manager-6d5d5d4d8-9pfhx       1/1     Running   0          7m37s
```

Curl the prometheus endpoint and confirm it is able to scrape metrics from the classifier pod.

```
$ curl <classifier-route>/prometheus

seldon_api_executor_server_requests_seconds_bucket{code="200",deployment_name="mymodel",method="post",predictor_name="mygroup",predictor_version="",service="predictions",le="0.005"} 0
```
#### Client Notebook Configuration 

Login to [OpenDataHub on the Operate-First Cloud](https://odh.operate-first.cloud/)

Run JupyterHub.

Start a terminal.

Clone this repo.

Open the [first notebook](https://github.com/bkoz/3d-image-classification/blob/master/01-inference-3d-image-classification.ipynb)



