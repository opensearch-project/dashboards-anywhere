[-](url) Start Date: 2022-06-09
- TTL: June 15th, 2022
- Champion: Huy Nguyen
- Main reviewer: Tao Liu
- Owner team: OpenSearch
- Stakeholders: GitHub Community
- OpenSearch Issue: #8 

# Executive Summary


## Problem Statement

While OpenSearch (abbreviated as **OS**), an open-source search and analytics
suite, and its corresponding visualization tool OpenSearch Dashboards 
(abbreviated as **OSD**) are powerful open-source tools, there has been a need 
by the community test out its features. Currently, the most commonly used method 
of demoing OS and OSD is by downloading their Docker images and running them 
on the user's local machine. 

![sample](https://user-images.githubusercontent.com/73027756/173409363-875057fe-6a2d-4b95-85cc-c8c3831d08c7.png)

While serviceable for some people, it was clear that a more 
convenient method was necessary to spread OS and OSD's capabilities to a wider 
customer audience.


## Goals

To make OS and OSD more convenient for our existing and prospective customers,
there were several key features that this OS/OSD application must implement:

- **Secure:** the application must be secure for users to gain trust in not 
    only the application but also OS/OSD. SSL certificates must be made and
    used.
- **Easily Accessible:** the application should not require the user to 
    download, sign-up, or any other extraneous step to play around with 
    OS/OSD's features.
- **Scaleable:** because this application showcases the capabilities of 
    OS/OSD, this application will be a first impression for many customers.
    Thus, the application should service them in a fast, secure, and reliable
    manner.


## Proposal

To address this need, a demo website we call OpenSearch Playground was 
proposed that would allow users to visit and start experimenting with OS/OSD. 
To meet our goal of an accessible, scaleable application, the application 
will leverage the speedy, open-source container orchestrator Kubernetes and 
Amazon Web Service's Elastic Kubernetes Service to enable fast, reliable 
delivery of OS/OSD to our customers.


# Who is Affected

The need for OpenSearch Playground site in particular, targets all of 
OpenSearch's customers, both existing and prospective. They will be the users 
who will learn and be curious about OS and OSD. Because this application will 
be for many of them a first hands-on experience, it is vital that OpenSearch Playground delivers the optimal experience of OS and OSD. 

OpenSearch Playground not only serves customers who will want to potentially utilize OS and OSD but also the contributors, who want a one-stop application 
to familiarize themselves with the site in order to start contributing or make
improvements to their existing work. Thus, the site serves a multifaceted 
purpose and targets a diverse audience.


# Design

Leveraging the power and scale of Amazon Web Service's **(AWS)** Elastic 
Kubernetes Service **(EKS)** as well as Route 53, OpenSearch Playground allows 
any prospective users to experiment with OS and OSD. OpenSearch Playground will 
be open to all (requiring no sign-ups) as a way to showcase the robust 
capabilities of the services offered by OS/OSD via a secure https connection.

![diagram_white](https://user-images.githubusercontent.com/73027756/173409473-3cc075f3-8ce6-4eb4-95e4-df6f13eb3899.png)

Creating OpenSearch Playground first requires the modification of the OS and OSD bundle configurations . OpenSearch and OpenSearch Dashboards initially require certain permissions to access features, like viewing the dashboards and interacting with sample data. Thus, the images were configured so that anonymous users could view only the features via the enabling of settings in the `config.yml`, `roles.yml`, `roles_mapping.yml`, and `opensearch_dashboards.yml`. 

Sample change for `config.yml`:
```
config:
  dynamic:
    http:
      anonymous_auth_enabled: true
```

Sample change for `roles.yml`:
```
opendistro_security_anonymous:
  reserved: true
  cluster_permissions:
    - 'cluster_monitor'
    - 'cluster:admin/ingest/pipeline/get'
    - 'cluster:admin/ingest/processor/grok/get'
    - 'cluster:admin/opendistro/ad/detector/search'
    - 'cluster:admin/opendistro/ad/detectors/get'
    - 'cluster:admin/opendistro/alerting/alerts/get'
    - 'cluster:admin/opendistro/alerting/destination/email_account/get'
    - 'cluster:admin/opendistro/alerting/destination/get'
    - 'cluster:admin/opendistro/alerting/monitor/get'
    - 'cluster:admin/opendistro/asynchronous_search/get'
    - 'cluster:admin/opendistro/ism/policy/get'
    - 'cluster:admin/opendistro/rollup/get'
    - 'cluster:admin/opendistro/reports/definition/get'
    - 'cluster:admin/opendistro/reports/instance/get'
    - 'cluster:admin/opensearch/observability/get'
    - 'cluster:admin/repository/get'
    - 'cluster:admin/script/get'
    - 'cluster:admin/snapshot/get'
    - 'cluster:monitor/task/get'
    - 'cluster_composite_ops_ro'
    - 'cluster:admin/opendistro/ad/result/search'
    - 'cluster:admin/opendistro/ad/tasks/search'
    - 'cluster:admin/opendistro/alerting/destination/email_account/search'
    - 'cluster:admin/opendistro/alerting/destination/email_group/search'
    - 'cluster:admin/opendistro/alerting/monitor/search'
    - 'cluster:admin/opendistro/ism/policy/search'
    - 'cluster:admin/opendistro/rollup/search'
  index_permissions:
    - index_patterns:
        - ".kibana"
        - ".kibana-6"
        - ".kibana_*"
        - ".opensearch_dashboards"
        - ".opensearch_dashboards-6"
        - ".opensearch_dashboards_*"
        - "*"
      allowed_actions:
        - 'indices:monitor/settings/get'
        - 'indices:monitor/stats'
        - 'indices:data/read*'
        - 'indices:admin/get'
```

Sample change for `roles_mapping.yml`:
```
opendistro_security_anonymous:
  backend_roles:
  - "opendistro_security_anonymous_backendrole"
```

Sample change for `opensearch_dashboards.yml`:
```
opendistro_security.auth.anonymous_auth_enabled: true
```

Another modification to OS and OSD is data ingestion. While OS and OSD have
sample data for users to play with, they currently require administrator 
access to load data into the dashboard. Because this project allows 
anonymous access, there needs to be a method of preloading the data before
the user visits the site. Otherwise, the user has no method of viewing OS
and OSD's capabilities. At the time of writing, there are two methods 
formulated to handle real-time data ingestion: leveraging existing Cypress
testing to gather sample data or implementing a data generator utility. A
decision will be posted in a subsequent issue.

In keeping with OS and OSD's open source nature, Kubernetes was chosen as 
the container orchestrator, since it was widely used and supported by many
cloud providers, particularly AWS. In order to maximize AWS's features, EKS
was used as a AWS kubernetes wrapper that seamlessly integrated Kubernete's
community-beloved features into the vast and powerful AWS cloud. 

After deploying the modified images to an EKS cluster, the last step is to
utilize a Domain Name System **(DNS)** in order to make OpenSearch/OpenSearch
Dashboards visible to all users with a friendly domain name. Thus, Amazon's 
Route 53 DNS web service was leveraged as an extremely reliable and cost 
effective way to route our users to OS/OSD. 


## Terminology and Acronyms

- **AWS:** Amazon Web Services
- **Container:** A software package that contains all libraries and 
    dependencies to run in any environment.
- **Cypress:** An end-to-end testing tool
- **Data Ingestion:** A process that transports data, typically with some
    transformations done to it, from one location to another
- **Docker:** A popular open-source container runtime environment.
- **DNS:** Domain Name System
- **EKS:** Elastic Kubernetes Service. A managed container service to run and
    scale Kubernetes applications in the cloud or on-premises.
- **Elasticsearch:** Another data analytics and search suite. OS forks from
    Elasticsearch version 7.10.
- **Image:** a static file wtih code that creates containers. Contains all
    dependencies to run an application anywhere.
- **Kubernetes:** A container orchestration tool to allow fast, scaleable
    deployment of containers via clusters.
- **OpenSearch Playground:** The name for the demo site
- **OS:** OpenSearch (not to be confused with Operating System). A search 
    and analytics suite that facilitates the ingesting, searching, 
    visualizing, and analyzing of data.
- **OSD:** OpenSearch Dashboards. A data visualization and user interface.
- **Route 53:** An AWS DNS web service. 


# Risks

The only point of consideration with OpenSearch Playground is its maintenance. 
As new versions of OS and OSD roll out, careful consideration must be shown as
to OpenSearch Playground's update strategy. One plan is to use GitHub Actions 
to automatically deploy when newer versions of OS/OSD release. This release 
will follow a blue-green deployment.


# Adoption Strategy

Since OpenSearch Playground is a demo site that deploys OS/OSD, close 
coordination should exist among the site, OS, and OSD to ensure compatibility 
for past and future versions.


# How this Scales

Since the site uses Kubernetes and EKS, OpenSearch Playground's scaleability 
is baked into its design. That being said, future requirements would enable
autoscaling of the cluster. Using several metrics, like CPU and memory
usage among others, the cluster can add or remove nodes as necessary. 


# Unresolved Questions and Future Features

OpenSearch Playground is primarily an end application that allows users to experiment with OS and OSD. However, there are future considerations to 
implement such as support for many versions of OS, OSD, and older versions of ElasticSearch. Future phases of the project include support for third party security authentication, a customized landing page for blogs, and potentially allowing users to ingest their own data. As the OS and OSD matures, so too 
will the future features of OpenSearch Playground.