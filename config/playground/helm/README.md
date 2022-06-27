# Helm Deployment Guide

## Summary

This document provides a guide to deploy OpenSearch (OS) and OpenSearch Dashboards (OSD) with custom configurations. Specifically, these configurations allow the deployment of OS and OSD such that anonymous users can access the website (read-only).

In the `/dev` folder, there are currently two `.yaml` files: 

- `helm-opensearch-dashboards.yaml` 
- `helm-opensearch.yaml`

These two files will be needed to setup a custom OS and OSD cluster.

## Prerequisites

Before you deploy OS/OSD using Helm, make sure you have done the following:

- Install and setup a [Kubernetes cluster](https://kubernetes.io/docs/setup/)
- Install [Helm](https://helm.sh/docs/intro/install/)
- (Optional): If using Amazon Web Service's (AWS) Elastic Kubernetes Service (EKS), install and configure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) with an [account](https://aws.amazon.com/free) and [credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html)

## Deploy OS/OSD Using Helm

To deploy the cluster with custom configurations, follow the below steps:

- Change directory into the config directory:

```cd config/playground/helm/{dev/prod}```

- Install OpenSearch Helm charts:

```
helm repo add opensearch https://opensearch-project.github.io/helm-charts/
helm repo update
```

- To check if OpenSearch Helm charts installed correctly, run the following command (it should look similar to the output below):

```
$ helm search repo opensearch
NAME                            	CHART VERSION	APP VERSION	DESCRIPTION                           
opensearch/opensearch           	2.1.0        	2.0.1      	A Helm chart for OpenSearch           
opensearch/opensearch-dashboards	2.1.0        	2.0.1      	A Helm chart for OpenSearch Dashboards
```

- Create a secret containing the username and password that allows OSD to connect with OSD:

```
kubectl create secret generic test-secret --from-literal='username=<your username>' --from-literal='password=<your password>'
```

- Install OpenSearch using `helm-opensearch.yaml`:

```
helm install <package name> opensearch/opensearch -f helm-opensearch.yaml
```

- Install OpenSearch Dashboards using `helm-opensearch-dashboards.yaml`:

```
helm install d opensearch/opensearch-dashboards -f helm-opensearch-dashboards.yaml
```

- To track progress of your pods, run the following command:

```kubectl get pods```

## Test and Run Deployment

The cluster should have OS and OSD deployed in your cluster. To verify and test them out, follow the steps below:

- To test out OS/OSD in your cluster, first get one of the OSD pod names:

~~~
$ kubectl get pods
NAME                                      READY   STATUS    RESTARTS   AGE
<opensearch dashboards name>              1/1     Running   0          2d22h
<opensearch dashboards name 2>            1/1     Running   0          2d22h
<opensearch dashboards name 3>            1/1     Running   0          2d22h
opensearch-cluster-master-0               1/1     Running   0          2d22h
opensearch-cluster-master-1               1/1     Running   0          2d22h
opensearch-cluster-master-2               1/1     Running   0          2d22h
~~~

- Then, `port-forward` one of them and navigate to your [localhost](http://localhost:5601/) (for this example, `<opensearch dashboards name>` was used):

```kubectl port-forward <opensearch dashboards name> 5601```