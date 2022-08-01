# Startup and Refresh Jobs

These jobs utilize all parts of the tooling necessary to programmatically startup: create indices, ingest those indices, and startup plugin resources using those indices. Not only will these jobs cover the startup tasks, but also the deletion of old indices and the creation and ingestion of new indices to refresh data.

## Pre-requisites

Before using this tool, make sure the required libraries as listed in `requirements.txt` are downloaded.

```
pip install requirements.txt
```

Because this tool requires the [`OpenSearch Python client`](https://opensearch-project.github.io/opensearch-py/), OpenSearch (OS) and OpenSearch Dashboards (OSD) must already be configured. Installations for OS can be found [here](https://opensearch.org/docs/latest/opensearch/install/index/) while installations for OSD can be found [here](https://opensearch.org/docs/latest/dashboards/install/index/).

In order to use default arguments, the tooling requires three environment variables to be defined:
- `HOST`
- `SAMPLE_DATA_USERNAME`
- `SAMPLE_DATA_PASSWORD`

## Setup

In order to use the tools, config files (as `.json` files) must be defined and placed in a specific directory, which by default, is `config/`. The following keys are necessary for the tooling:
- `plugin` (string): The plugin name in which to initialize and use the indices; currently, the only fully implemented option is `anomaly_detection`
- `ingest_args` (JSON key-value): The configurations necessary to call the `ingest()` function (see `sample_data_ingestor/README.md` for more information on all the arguments)
    - One necessary argument is `data_template` and for information regarding the template, refer to `sample_data_generator/README.md`
- `days_before` (int): how far back the data generated will go (e.g. if `"days_before": 7`, then data generated will have timestamps starting from one week ago until today); If data does not have timestamps, leave as `"days_before": 0`.
- `days_after` (int): how far forward the data generated will go (e.g. if `"days_after": 7`, then data generated will have timestamps that continue from today until one week from now); If data does not have timestamps, leave as `"days_before": 0`.
- `index_body` (JSON key-value): The configurations necessary to [create an index](https://opensearch.org/docs/latest/opensearch/rest-api/index-apis/create-index/)
- `create_payload` (JSON key-value): The configurations necessary to create a plugin. For instance, see [this page](https://opensearch.org/docs/latest/monitoring-plugins/ad/api/#create-anomaly-detector) for configurations for setting up an anomaly detector.

### Example Config File
```
{
    "plugin": "anomaly_detection",
    "ingest_args": {
        "index_name" : "cpu-usage-logs",
        "data_template" : {
            "date": "unix_time",
            "average_cpu_usage": [
                "integer", 20, 30
            ]
        },
        "mapping" : false,
        "file_provided": false,
        "chunk" : 5,
        "timestamp" : "date",
        "minutes" : 3,
        "number": 1,
        "max_bulk_size": 100000,
        "anomaly_detection_trend": [
            {
                "data_trend": "AverageTrend",
                "feature" : "average_cpu_usage",
                "anomaly_percentage" : 0.001,
                "avg_min" : 20,
                "avg_max" : 30,
                "abs_min" : 0,
                "abs_max" : 100
            }
        ]
    },
    "days_before": 7,
    "days_after": 7,
    "index_body": {
        "settings": {
            "index": {
                "number_of_shards": 4
            }
        },
        "mappings": {
            "properties": {
                "date": {"type": "date"},
                "average_cpu_usage": {"type": "integer"}
            }
        }
    },
    "create_payload": {
        "name": "cpu-usage-detector",
        "description": "Monitors cpu usage every 10 minutes",
        "time_field": "date",
        "indices": [
            "test-index"
        ],
        "feature_attributes": [
            {
            "feature_name": "average_cpu_usage",
            "feature_enabled": true,
            "aggregation_query": {
                "test": {
                "avg": {
                    "field": "average_cpu_usage"
                }
                }
            }
            }
        ],
        "filter_query": {
            "match_all": {}
        },
        "detection_interval": {
            "period": {
            "interval": 10,
            "unit": "Minutes"
            }
        },
        "window_delay": {
            "period": {
            "interval": 1,
            "unit": "Minutes"
            }
        }
    }
}
```

In the example above, this config job will cover the resources necessary to start an sample anomaly detector. Data with a `"timestamp"` (called as `"date"`) and `"average_cpu_usage"` are being generated. Because time-series data is being generated, the `"minutes"` key is specified. In this example, `"minutes"` was set to 3, meaning that for a given day with `1440` minutes, there will be `1440/3` or `480` data points. As for `"average_cpu_usage"`, it will be an integer representing the percentage, and will follow a straight-line average trend (specified in `"anomaly_detection_trend"`). Essentially, `"average_cpu_usage"` will mostly fall between `20%` and `30%` with some anomalies between `0%` and `100%`. Anomalies will have a `0.1%` of being generated (or 0.001). Finally, this data will simulate two weeks worth of documents that occurred one week ago (specified in `"days_before"`) and one week in the future (specified in `"days_after"`).

Using the same configurations, refreshing the data will also occur. The refresh job will scan for any indices that are older than `"days_before"`, or a week ago, and delete them. Then, the refresh job will generate data (if the data doesn't exist for a given date) that occurs up to `"days_after"`, or a week in the future. In other words, if this refresh job is to be run once everyday, the job deletes indices older than a week and creates future data indices up to a week from now, thus refreshing data.

## Commands

```
$ python3 startup_job.py

$ python3 refresh_job.py
```

As these scripts provide the entry point for executing the aforementioned tasks, the script provides several (optional) arguments for running both scripts:

- `-h, --help`: Shows the help message and exits program
- `-host HOST`: The hostname (without the scheme and top-level domain); The default is the environment variable `HOST`
-  `-username USERNAME`: The username of OpenSearch role with CRUD permissions (typically the admin); The default is the environment variable `SAMPLE_DATA_USERNAME`
- `-password PASSWORD`: The password of OpenSearch role with CRUD permissions (typically the admin); The default is the environment variable `SAMPLE_DATA_PASSWORD`
- `-port PORT`: The port number in which OpenSearch will listen to; The default is 9200
- `-config_path CONFIG_PATH`: The directory where plugin configurations are to be found and used by the tool; The default is `config/`

```
$ python3 startup_job.py -host playground -username admin -password admin
```

The example above executes the startup job with the host `playgound`, the username as `admin`, and the password as `admin`.

## Startup Job

This job covers the creation of indices, the ingestion of sample data into those indices, and the creation of plugin resources using those indices. There is only one method for this script:

- `startup_job()`: Given a path where plugin config files are located, an `Authentication` object (see `sample_data_authentication/README.md` for more details), an `OpenSearch Python client` object, and a URL, execute the startup tasks
    - **Arguments:**
        - `config_path` (string): The directory path in which the plugin config json files are located (currently this job script only accepts `.json` config files); by default, the script looks in the `/config` directory
        - `url` (string): The base url in which various API requests can be made to OpenSearch; this url will be utilized for the plugin creation and various other CRUD operations. By default, `url` prepends `https://` to `host`
        - `header` (`Authentication` object): The Authentication object used to create and return request headers; by default, the job uses `BasicAuthentication` authentication (essentially, just user credentials for the user role with CRUD permissions)
        - `client` (`OpenSearch Python client` object): The client needed to perform various index CRUD operations. By default certificate verification is set to `False`.

## Refresh Job

This job covers the refreshing of data, specifically the deletion of old indices (defined in the config file), the creation of new indices, and the ingestion of sample data into those indices. There is only one method for this script.

- `refresh_job()`: Given a path where plugin config files are located and an `OpenSearch Python client` object, execute the refresh tasks
    - **Arguments:**
        - `config_path` (string): The directory path in which the plugin config json files are located (currently this job script only accepts `.json` config files); by default, the script looks in the `/config` directory
        - `client` (`OpenSearch Python client` object): The client needed to perform various index CRUD operations. By default certificate verification is set to `False`.
