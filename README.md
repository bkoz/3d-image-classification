# Classification of 3D Medical images 

## Deployed with seldon using OpenShift s2i

Deploy a custom image using OpenShift s2i and Seldon. 
Based on [Brian's blog post](https://www.openshift.com/blog/serving-machine-learning-models-on-openshift-part-1). 
Also read this [medium article](https://towardsdatascience.com/to-serve-man-60246a82d953) 
by Alexander Sack that is explained well. 
[Additional](https://docs.primehub.io/docs/model-deployment-tutorial-package-image) info.

## Steps

### Create and start a new build.

```
oc new-build --strategy docker --docker-image registry.redhat.io/ubi8/python-36 --name mymodel -l app=mymodel --binary

oc start-build mymodel --from-dir=. --follow

```

Edit `mymodel-seldon-deploy.yaml` to match the environment and deploy.

```
oc apply -f resources/mymodel-seldon-deploy.yaml

oc expose svc <svc-name>
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
