# OS/OSD GitHub Action Guide

## Summary

This document provides the guidance for the useage of GitHub actions.

The current workflows folder contains one deployment workflow(os-osd-deployment.yml) and two reusable workflows(deployment-template.yml and function-tests-template.yml). os-osd-deployment workflow will call deployment-template and function-test-template with required inputs and secrets for the deployment and tests.

- os-osd-deployment.yml
- deployment-template.yml
- function-tests-template.yml

## Prerequisites

- GitHub account
- Public repository
- GitHub action workflows


## Detail workflows

> os-osd-deployment.yml: 
>> This is a mainly deployment workflow for OpenSearch and OpenSearch Dashboards, it includes dev and prod two environment. 

> deployment-template.yml:
>> This is a reusable workflow for deployment. It requires couple inputs and secrets. The list of required inputs and secrets.
>> - inputs: helm-repo, it is offical helm release location of OpenSearch and OpenSearch Dashboards.
>> - inputs: deploy-env, it is the variable for environment, like as dev or prod.
>> - secrets: access-key-id, it is access id for EKS cluster.
>> - secrets: secret-access-key, it is access key for EKS cluster.
>> - secrets: region, it is cluster region.
>> - secrets: kube-config, it is client kube configuration which was used to connect to EKS cluster.

> function-tests-template.yml:
>> This is a reusable function tests workflows for OpeanSearch Dashboards. The required inputs and secrets as following:
>> - inputs: endpoint, the OpenSearch Dashboard endpoint.
>> - secrets: osd-user, the write access user of OpenSearch Dashboards.
>> - secrets: osd-user-password, the write access user's password for OpenSearch Dashboards.


## Appendix

- GitHub workflow: https://docs.github.com/en/actions/using-workflows/about-workflows

- Reusable workflow : https://docs.github.com/en/actions/using-workflows/reusing-workflows
