# Metrics Configuration Guide

## Summary

This document provides a guide to configure [fluentbit](https://docs.fluentbit.io/manual) and Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) which process EKS cluster logs to OpenSearch and trigger health check CronJob.

The current metrics folder contains four functions, the detail as following:
> CronJobs
>> This folder contains Kubernetes CronJob. `cronjob-healthcheck.yaml` was used to check health for the playground site. The health check response memtrics will be piped to OpenSearch by fluent-bit log processor. 

> Fluent-Bit
>> This folder contains the configuration of fluent-bit, `fluent-bit.yaml` was used for processing the metrics log from Playground site to OpenSearch. 

> Logstash
>> This folder contains the configuration of logstash, the configuration files were used for processing the cluster metrics log from EKS cluster to Playground OpenSearch. Please refer to [Workshop Logstash](https://catalog.us-east-1.prod.workshops.aws/workshops/c87214bf-11ea-46b7-82d9-4d934c2a7f53/en-US/logs/logstash).

> Tracing
>> This folder contains the configuration of tracing, the configuration files were used for processing the observability trace log from sample applicaton to Playground OpenSearch. Please refer to [Workshop Tracing](https://catalog.us-east-1.prod.workshops.aws/workshops/c87214bf-11ea-46b7-82d9-4d934c2a7f53/en-US/logs/tracing).

## Prerequisites

- Install and setup a [Kubernetes cluster](https://kubernetes.io/docs/setup/)

## Deploy And Delete Fluent-Bit
The `./metrics/fluent-bit/fluent-bit.yaml` file was used for processing logs from Playground to AWS OpenSearch, you need to pre-config [IAM roles](https://www.eksworkshop.com/intermediate/230_logging/config_es/) before deploying the Fluent-bit and replace `{endpoint} and {region}` in the `fluent-bit.yaml`

```
# Deploys fluent-bit to EKS cluster
kubectl apply -f fluent-bit.yaml

# Deletes fluent-bit from EKS cluster
kubectl delete -f fluent-bit.yaml
```
## Deploy And Delete CronJobs
The `./metrics/cronjobs/cronjob-healthcheck.yaml` file was used to trigger heath check CronJob for the Playground site. The heartbeat reponse will be used for the monitor and alert. 

You need to pre-config [secrets](https://kubernetes.io/docs/concepts/configuration/secret/) (USER_NAME/PASSWORD/DOMAIN) before deploying the CronJobs. The secrets were used for communicating playground site.

```
# Creates CronJob for health check
kubectl create -f cronjob-healthcheck.yaml
kubectl delete cronjob healthcheck-cronjob
```

## Deploy And Delete Logstash
You need to replace the `${OSD_USER}` and `${OSD_USER_PASSWORD}` in the `logstash.yaml` file, this file was used for logstash deployment.

```
# Deploy Logstash
kubectl create ns logstash
kubectl create -f logstash-configmap.yaml
kubectl apply -f logstash.yaml

# Delete Logstash
kubectl delete ns logstash
```
## Deploy And Delete Tracing
You need to replace the `${OSD_USER}` and `${OSD_USER_PASSWORD}` in the `otel-config.yaml` file, this file was used for tracing deployment. 

```
# Deploy Tracing
kubectl apply -f jaeger-agent.yaml
kubectl create -f otel-config.yaml
kubectl apply -f otel-collector.yaml
kubectl apply -f data-prepper.yaml

# Delete Tracing
kubectl delete -f jaeger-agent.yaml
kubectl delete -f otel-config.yaml
kubectl delete -f otel-collector.yaml
kubectl delete -f data-prepper.yaml```
```


## Appendix
- [Fluent-Bit](https://docs.fluentbit.io/manual) is a logging processor and forwarder that’ll be used to take the raw logs and send them up to OpenSearch for processing.
- [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) creates jobs on a repeating schedule.
- [Data Prepper](https://opensearch.org/docs/1.2/clients/data-prepper/index/) is a server side data collector capable of filtering, enriching, transforming, normalizing and aggregating data for downstream analytics and visualization.