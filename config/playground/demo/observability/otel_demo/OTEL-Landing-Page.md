
![](https://raw.githubusercontent.com/opensearch-project/.github/main/profile/banner.jpg)
# OpenSearch Observability OTEL Demo

Welcome to the [OpenSearch](https://opensearch.org/docs/latest) OpenTelemetry [Demo](https://opentelemetry.io/docs/demo/) documentation, which covers how to install and run the demo, and some scenarios you can use to view OpenTelemetry in action.

## Purpose
The purpose of this demo is to demonstrate the different capabilities of OpenSearch Observability to investigate and reflect your system.

![](../../../.github/img/DemoFlow.png)

### Services
[OTEL DEMO](https://opentelemetry.io/docs/demo/services/) Describes the list of services that are composing the Astronomy Shop.

The main services that are open to user interactions:

- [Dashboards](https://otel.playground.opensearch.org/)

- [Demo Shop](https://shop.otel.playground.opensearch.org/)

---

### Screenshots

_**The Shop**_


![Shop](https://opentelemetry.io/docs/demo/screenshots/frontend-1.png)



_**The load generator**_


![](https://opentelemetry.io/docs/demo/screenshots/load-generator-ui.png)

---

### [Integrations](https://otel.playground.opensearch.org/app/integrations#/available)
![](https://github.com/opensearch/opensearch-catalog/blob/otel-demo-integration/integrations/observability/otel-demo/static/dashboard1.png?raw=true)

The integration service is a list of pre-canned assets that are loaded in a combined manner to allow users the ability for simple and automatic way to discover and review their services topology.

These [OTEL demo](https://github.com/opensearch-project/opensearch-catalog/pull/91) integrations contain the following assets:
- components & index template mapping
    - [traces mapping](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/create-template/ss4o_traces_template)
    - [logs mapping](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/create-template/ss4o_logs_template)
    - [metrics mapping](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/create-template/ss4o_metrics_template)

- Index Patterns
    - [traces](https://otel.playground.opensearch.org/app/management/opensearch-dashboards/indexPatterns/)
    - [logs](https://otel.playground.opensearch.org/app/management/opensearch-dashboards/indexPatterns/)
    - [metrics](https://otel.playground.opensearch.org/app/management/opensearch-dashboards/indexPatterns/)

- Index Aliases
    - [traces](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/aliases)
    - [logs](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/aliases)
    - [metrics](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/aliases)

- datasources
    - [Prometheus](https://otel.playground.opensearch.org/app/datasources#/manage/prometheus)
- data-stream & indices
    - [Traces / Data-prepper](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/otel-v1-apm-span-000001)
    - [Traces / Jaeger](hhttps://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/jaeger-span-2023-12-13)
    - [Services / Data-prepper](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/otel-v1-apm-service-map)
    - [Services / Jaeger](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/jaeger-service-2023-12-13)
    - [Metrics / Data-prepper ](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/otel-metrics-2023.12.13)
    - [Log-Events / Data-prepper ](https://otel.playground.opensearch.org/app/opensearch_index_management_dashboards#/index-detail/otel-events-2023.12.13)


- dashboards
    - [OTEL Architecture](https://otel.playground.opensearch.org/app/dashboards#/view/67e37e40-f750-11ed-b6d0-850581e4a72d)
    - [System-Wide AMP](https://otel.playground.opensearch.org/app/dashboards#/view/b0d09c20-9893-11ee-8bb8-69dd3b5541dd)
---
### Ingestion
The ingestion capabilities for OpenSearch is to be able to support multiple pipelines:
- [Data-Prepper](https://github.com/opensearch-project/data-prepper/) is an OpenSearch ingestion project that allows ingestion of OTEL standard signals using Otel-Collector
- [Jaeger](https://opensearch.org/docs/latest/observing-your-data/trace/trace-analytics-jaeger/) is an ingestion framework which has a build in capability for pushing OTEL signals into OpenSearch
- [Fluent-Bit](https://docs.fluentbit.io/manual/pipeline/outputs/opensearch) is an ingestion framework which has a build in capability for pushing OTEL signals into OpenSearch
