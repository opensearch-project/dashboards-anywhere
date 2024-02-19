# Jenkins Configuration Guide

## Summary

This document provides a guide to configure a Jenkins file to cover tests with selected OpenSearch versions. This Jenkins instance is related to the [RFC] OpenSearch Dashboard Version Decoupling's matrix collection section, which can be found [here](https://github.com/opensearch-project/OpenSearch-Dashboards/issues/5804). This will trigger unit, integration, and functional (Selenium) tests against all different versions of OpenSearch specific to the version of OpenSearch Dashboards.

## Prerequisites

- Jenkins pipeline
- [OpenSearch Dashboards Reproistiry](https://github.com/opensearch-project/OpenSearch-Dashboards)

## Run Jenkins Pipeline

This Jenkins file includes the default version parameter `defaultValue: '1.0.0,1.1.0,1.2.0,1.3.0,2.3.0,2.5.0,2.7.0,2.9.0,2.11.0'` for selected OpenSearch versions. You can override this parameter to any OpenSearch version as needed. It will kick off OpenSearch Dashboards tests against the selected OpenSearch versions in parallel with ciGroups.


## Test Results
The output test results will look like the following 

| Package                    	|   Duration 	| Fail  	| (diff) 	| Skip 	| (diff) 	| Pass 	| (diff) 	| Total 	| (diff) 	|
|----------------------------	|-----------:	|------:	|-------:	|-----:	|-------:	|-----:	|-------:	|------:	|-------:	|
| Functional Tests For 1.0.0 	| 2 hr 4 min 	|     0 	|        	|   30 	|     30 	|  601 	|    582 	|   631 	|    612 	|
| Functional Tests For 1.1.0 	| 2 hr 3 min 	|     0 	|        	|   30 	|     30 	|  601 	|    582 	|   631 	|    612 	|
