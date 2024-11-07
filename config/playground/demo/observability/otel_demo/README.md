# Opensearch OTEL Demo Architecture
This document will review the OpenSearch architecture for the [OTEL demo](https://opentelemetry.io/docs/demo/) and will review how to use the new Observability capabilities
implemented into OpenSearch.
---
This diagram provides an overview of the system components, showcasing the configuration derived from the OpenTelemetry Collector (otelcol) configuration file utilized by the OpenTelemetry demo application.

Additionally, it highlights the observability data (traces and metrics) flow within the system.

![](img/otelcol-data-flow-overview.png)

---
[OTEL DEMO](https://opentelemetry.io/docs/demo/architecture/) Describes the list of services that are composing the Astronomy Shop.

They are combined of:
 - [Accounting](https://opentelemetry.io/docs/demo/services/accounting/)
 - [Ad](https://opentelemetry.io/docs/demo/services/ad/)
 - [Cart](https://opentelemetry.io/docs/demo/services/cart/)
 - [Checkout](https://opentelemetry.io/docs/demo/services/checkout/)
 - [Currency](https://opentelemetry.io/docs/demo/services/currency/)
 - [Email](https://opentelemetry.io/docs/demo/services/email/)
 - [Feature Flag](https://opentelemetry.io/docs/demo/services/feature-flag/)
 - [Fraud Detection](https://opentelemetry.io/docs/demo/services/fraud-detection/)
 - [Frontend](https://opentelemetry.io/docs/demo/services/frontend/)
 - [Kafka](https://opentelemetry.io/docs/demo/services/kafka/)
 - [Payment](https://opentelemetry.io/docs/demo/services/payment/)
 - [Product Catalog](https://opentelemetry.io/docs/demo/services/product-catalog/)
 - [Quote](https://opentelemetry.io/docs/demo/services/quote/)
 - [Recommendation](https://opentelemetry.io/docs/demo/services/recommendation/)
 - [Shipping](https://opentelemetry.io/docs/demo/services/shipping/)
 - [Fluent-Bit]() *(Nginx's otel log exported)* 
 - [Integrations]() *(Pre-canned OpenSearch assets)* 
 - [DataPrepper]() *(OpenSearch's ingestion pipeline)*

Backend supportive services
 - [Load Generator]()
   - See [description]()
 - [Frontend Nginx Proxy]() *(Replacement for _Frontend-Proxy_)*
 - [OpenSearch]()
 - [Dashboards]()
 - [Prometheus]()
 - [Feature-Flag]()

### Services Topology
The next diagram shows the docker compose services dependencies

![](img/docker-services-topology.png)
---

## Purpose
The purpose of this demo is to demonstrate the different capabilities of OpenSearch Observability to investigate and reflect your system.

### Ingestion 
The ingestion capabilities for OpenSearch is to be able to support multiple pipelines:
  - [Data-Prepper](https://github.com/opensearch-project/data-prepper/) is an OpenSearch ingestion project that allows ingestion of OTEL standard signals using Otel-Collector
  - [Jaeger](https://opensearch.org/docs/latest/observing-your-data/trace/trace-analytics-jaeger/) is an ingestion framework which has a build in capability for pushing OTEL signals into OpenSearch
  - [Fluent-Bit](https://docs.fluentbit.io/manual/pipeline/outputs/opensearch) is an ingestion framework which has a build in capability for pushing OTEL signals into OpenSearch

### Integrations -
The integration service is a list of pre-canned assets that are loaded in a combined manner to allow users the ability for simple and automatic way to discover and review their services topology.

These (demo-sample) integrations contain the following assets:
 - components & index template mapping
 - datasources 
 - data-stream & indices
 - queries
 - dashboards
   
Once they are loaded, the user can imminently review the OTEL demo services and dashboards that reflect the system state.
 - [Nginx Dashboard]() - reflects the Nginx Proxy server that routes all the network communication to/from the frontend
 - [Prometheus datasource]() - reflects the connectivity to the prometheus metric storage that allows us to federate metrics analytics queries
 - [Logs Datastream]() - reflects the data-stream used by nginx logs ingestion and dashboards representing a well-structured [log schema](../src/integrations/mapping-templates/logs.mapping)

Once these assets are loaded - the user can start reviewing its Observability dashboards and traces

![Nginx Dashboard](img/nginx_dashboard.png)

![Prometheus Metrics](img/prometheus_federated_metrics.png)

![Trace Analytics](img/trace_analytics.png)

![Service Maps](img/services.png)

![Traces](img/traces.png)

![ServiceGraph](img/service-graph.png)
---

### **Scenarios**

How can you solve problems with OpenTelemetry? These scenarios walk you through some pre-configured problems and show you how to interpret OpenTelemetry data to solve them.

- Generate a Product Catalog error for GetProduct requests with product id: OLJCESPC7Z using the Feature Flag service
- Discover a memory leak and diagnose it using metrics and traces. Read more

### **Reference**
Project reference documentation, like requirements and feature matrices [here](https://opentelemetry.io/docs/demo/#reference)

