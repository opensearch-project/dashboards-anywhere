# Sample Data Generator and Ingestion Tool Deployment

Sourcing sample data is a pain point for developers and having sample data to play with is necessary for the customer. Enter this sample data & ingestion tool, which is ready to run as a container in Kubernetes.

## Overview

This directory contains all the files necessary to generate and ingest data into plugins (like the Anomaly Detector). Below will cover the process for deploying this in Playground as a [Kubernetes Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/) and [Kubernetes Cronjob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/). Alternatively, there are instructions for running this tool on a local environment as well.

## Running tooling on a local environment

Before using this tool, make sure the required libraries as listed in `requirements.txt` are downloaded.

```
pip install requirements.txt
```

Because this tool requires the [`OpenSearch Python client`](https://opensearch-project.github.io/opensearch-py/), OpenSearch (OS) and OpenSearch Dashboards (OSD) must already be configured. Installations for OS can be found [here](https://opensearch.org/docs/latest/opensearch/install/index/) while installations for OSD can be found [here](https://opensearch.org/docs/latest/dashboards/install/index/). This tooling assumes that OpenSearch and OpenSearch Dashboards are deployed on a Kubernetes cluster using [Helm](https://helm.sh/docs/intro/install/). Thus ensure [`kubectl`](https://kubernetes.io/docs/tasks/tools/) is installed and a [Kubernetes cluster](https://kubernetes.io/docs/setup/) is configured.

In order to use default arguments, the tooling requires three environment variables to be defined:
- `SAMPLE_DATA_HOST`
- `SAMPLE_DATA_USERNAME`
- `SAMPLE_DATA_PASSWORD`

To use this tool locally, set `SAMPLE_DATA_HOST` to `localhost`. Then, follow this sequence of commands:
```
kubectl get pods
```

Then, copy one of the OpenSearch pods. For this example, we will use `opensearch-cluster-leader-0`:
```console
$ kubectl get pods
NAME                                               READY   STATUS      RESTARTS   AGE
dashboards-opensearch-dashboards-cd954cd4b-7hdsk   1/1     Running     0          10d
dashboards-opensearch-dashboards-cd954cd4b-sp74n   1/1     Running     0          10d
opensearch-cluster-leader-0                        1/1     Running     0          10d
opensearch-cluster-leader-1                        1/1     Running     0          10d
opensearch-cluster-leader-2                        1/1     Running     0          10d
opensearch-cluster-leader-3                        1/1     Running     0          10d
opensearch-cluster-leader-4                        1/1     Running     0          10d
```

Finally, `port-forward` this opensearch pod to port `9200`.
```
kubectl port-forward opensearch-cluster-leader-0 9200
```

To use this tooling, from this directory, navigate to `sample_data_jobs` and run
```
python3 startup_job.yaml

python3 refresh_job.yaml
```

To run the startup job and refresh job, respectively. See `sample_data_jobs/README.md` for details over arguments.

## Deploying tooling as a container

In order to deploy this tooling to Playground, first ensure that [`kubectl`](https://kubernetes.io/docs/tasks/tools/) is installed. If you are not using Playground but instead another [Kubernetes cluster](https://kubernetes.io/docs/setup/), install [Helm](https://helm.sh/docs/intro/install/) and then install [OpenSearch using Helm](https://opensearch.org/docs/latest/opensearch/install/helm/) as well as [OpenSearch Dashboards using Helm](https://opensearch.org/docs/latest/dashboards/install/helm/).

Once `kubectl` is installed and the Kubernetes cluster is running, first configure secrets so the container can pull credentials from the cluster.

```
kubectl create secret generic sample-data-secret --from-literal='username=<admin username>' --from-literal='password=<admin password>' --from-literal='host=opensearch-cluster-leader'
```

Then, from this directory, change directory into the job and cronjob deployment files and deploy them.

For the sample data startup job:
```
cd ../../../config/playground/job

kubectl apply -f startup_deployment.yaml
```

This job should start immediately once it has been deployed.

To remove this job, call:
```
kubectl delete job sample-data-startup-job
```

For the sample data refresh cronjob:
```
cd ../../../config/playground/cronjob

kubectl apply -f refresh_deployment.yaml
```

This job should execute once everyday at 1 a.m. UTC.

To remove this job, call:
```
kubectl delete cronjob sample-data-refresh-cronjob
```

### Deploying a custom image

If you want customization for this tooling, first ensure [Docker](https://docs.docker.com/get-docker/) is installed and some registry is configured. After making revisions to the tooling, modify the deployment files. To navigate to those files, from this directory, change directory:

For the startup job
```
cd ../../../config/playground/job
```

And for the refresh cronjob
```
cd ../../../config/playground/cronjob
```

And modify the image name to your specified URI:
```
template:
        spec:
          containers:
            - name: sample-data-refresh-cronjob
              image: <IMAGE URI>
```

Then, once both deployment file image URIs are configured, from this tooling directory, run:
```
docker buildx build --platform linux/386 -t <IMAGE REPO URI> --push .
```

to push the custom image into the registry of your choice. Then the process for deploying to a cluster should be very similar to [Deploying tooling as a container](#deploying-tooling-as-a-container).