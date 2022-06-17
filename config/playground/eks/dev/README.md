# Terraform - Elastic Kubernetes Getting Started Guide

## Documentation

The full configuraiton of Terraform [resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

We leverage the following terraform resources to create EKS(Elastic Kubenetes Service) cluster
- [Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_cluster)
- [Node group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_node_group)
- [Subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet)


## Prerequisites

Before run the Terraform commands, you must meet the following prerequisites:

- The Terraform CLI (1.2.0+) installed - [Install Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started)
- The [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed
- [AWS account](https://aws.amazon.com/free) and [associated credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) that allow you to create resources- It hosts the EKS cluster and related resources.

## Deploy EKS via Trraform

The main steps to deploy EKS cluster with terraform configuration file as following:

- Change into config directory, which stores terraform configuration file (*.tf). 
    ```
    cd config/playground/eks/dev
    ```

- Initialize: Install the required Terraform providers defined in the configuration
    ```
    terraform init
    ```
- Plan: Preview the changes Terraform will make and validate the configuration
    ```
    terraform plan
    ```
- Apply: Make the changes to your infrastructure and create EKS cluster
    ```
    terraform apply
    ```
## Validate the newly created EKS cluster

Copy the output of Kubeconfig from above `terraform apply` step to local Kubernetes connection configuration,
the default config path $HOME/.kube/config

Run kubectl command to againest the newly created EKS cluster, it should return the nodes defined in the configuration

```
kubectl get nodes
``` 