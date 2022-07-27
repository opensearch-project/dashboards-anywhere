# Sample Data Tooling: Ingestion

## Pre-requisites:

Before using this tool, make sure the required libraries as listed in `requirements.txt` are downloaded. Because this tool requires the `OpenSearch Python client`, OpenSearch (OS) and OpenSearch Dashboards (OSD) must already be configured. Installations for OS can be found [here](https://opensearch.org/docs/latest/opensearch/install/index/) while installations for OSD can be found [here](https://opensearch.org/docs/latest/dashboards/install/index/). 

## Overview

Assuming data is on hand (if data needs to be generated see the `sample_data_generator` directory), now what? Ingest it, of course! 

This tool handles the ingestion of documents into a desired index name. Given a data template (or user provided data file), this tool will either generate the data or simply read from the data file and ingest them into an index with the `BULK` API. 

## Methods

- `ingest_from_user_data()`: Given a filename, this function will read from the file and return a list of documents read.
    - **Arguments:**
        - `filename` (string): The filename of the data file. This can be a `.json` or `.csv` file, zipped or unzipped (with the extension `.gz`).
    - **Returns:**
        - A list of documents read from the file. Note that timestamp fields will not be updated in this function.
- `ingest_validation()`: Given various arguments, this function will validate input and raise errors if input is invalid.
    - **Arguments (all optional):**
        - `client` (OpenSearch object): The OpenSearch object used to make the API call to OS.
        - `data_template` (string or dict): The template used to generate documents. See the generation tool for reference.
        - `index_name` (string): The name of the target index in which documents will be ingested.
        - `mapping` (boolean): Whether the `data_template` is a JSON [mapping](https://opensearch.org/docs/latest/opensearch/mappings/).
        - `file_provided` (boolean): Whether the `data_template` is a file that contains the template to generate documents.
        - `number` (integer): How many documents to generate (if `minutes` was specified, `number` was automatically calculated as the number of minutes per day divided by `minutes`).
        - `minutes` (integer): The time interval between each successive data point (e.g. if minutes = 2, this tool will generate documents with timestamps that are 2 minutes apart from one another).
        - `chunk` (integer): The maximum amount of documents that can be ingested per `BULK` call.
        - `timestamp` (string): The *field name* which contains a timestamp. For the purposes of this tool, only `unix time` (in milliseconds) is supported.
        - `current_date` (datetime): The date at which documents are generated (e.g. if the date was today, then documents will be generated with timestamp fields containing today's date in `unix time` milliseconds).
        - `max_bulk_size` (integer): The maximum size in bytes of the request body to ingest documents for one `BULK` call (`chunk` also deals with limiting document ingestion)
        - `anomaly_detection_trend` (dict): The dictionary containing config variables to create trends in document data (see [Generating Data Trends](#generating-data-trends) for more information).
    - **Returns:**
        - This function does not return anything.
- `build_request_body()`: Given various arguments, this function will return a tuple containing the request body (as a dict) and the current index of the dataset it has already added (see "**Returns**" for more information)
    - **Arguments:**
        - `file_provided` (boolean): Whether the `data_template` is a file that contains the template to generate documents.
        - `index_name` (string): The name of the target index in which documents will be ingested.
        - `timestamp` (string): The *field name* which contains a timestamp. For the purposes of this tool, only `unix time` (in milliseconds) is supported.
        - `minutes` (integer): The time interval between each successive data point (e.g. if minutes = 2, this tool will generate documents with timestamps that are 2 minutes apart from one another).
        - `chunk` (integer): The maximum amount of documents that can be ingested per `BULK` call.
        - `current_index` (integer): The current index of the dataset whose document will be added to the request body (for example, if the `dataset` has 50 entries and `current_index` is 23, then the function will add documents beginning from `dataset[23]` onwards)
        - `dataset` (list): The entire list of documents to be ingested.
        - `max_bulk_size` (integer): The maximum size in bytes of the request body to ingest documents for one `BULK` call (`chunk` also deals with limiting document ingestion)
    - **Returns:**
        - This function returns a tuple containing the request body (for `ingest()` to then make the `BULK` API call) and the next index for a subsequent call to look at (i.e. after an iteration of the `dataset` list).
- `ingest()`: Given various arguments, this function will ingest documents into the target index and return a list of the documents that were ingested.
    - **Arguments:**
        - `client` (OpenSearch object): The OpenSearch object used to make the API call to OS.
        - `data_template` (string or dict): The template used to generate documents. See the generation tool for reference.
        - `index_name` (string): The name of the target index in which documents will be ingested.
        - `mapping` (boolean): Whether the `data_template` is a JSON [mapping](https://opensearch.org/docs/latest/opensearch/mappings/).
        - `file_provided` (boolean): Whether the `data_template` is a file that contains the template to generate documents.
        - `number` (integer): How many documents to generate (if `minutes` was specified, `number` was automatically calculated as the number of minutes per day divided by `minutes`).
        - `minutes` (integer): The time interval between each successive data point (e.g. if minutes = 2, this tool will generate documents with timestamps that are 2 minutes apart from one another).
        - `chunk` (integer): The maximum amount of documents that can be ingested per `BULK` call.
        - `timestamp` (string): The *field name* which contains a timestamp. For the purposes of this tool, only `unix time` (in milliseconds) is supported.
        - `current_date` (datetime): The date at which documents are generated (e.g. if the date was today, then documents will be generated with timestamp fields containing today's date in `unix time` milliseconds).
        - `max_bulk_size` (integer): The maximum size in bytes of the request body to ingest documents for one `BULK` call (`chunk` also deals with limiting document ingestion)
        - `anomaly_detection_trend` (dict): The dictionary containing config variables to create trends in document data.
    - **Returns:**
        - This function returns a list of the documents that were ingested to the `index_name`

## Generating Data Trends

Sometimes data cannot be generated entirely randomly. For certain types of data, such as log data, there is a need to simulate a trend. While this can be accomplished for numeric data by specifying a "min" and "max" range, this may not cover the case when irregularities, or anomalies, occur. In this case, data being generated needs to not only simulate a trend but also model anomalies. This tool provides support for this (and support for users to define their own trend).

```
data_template = { 
    date = "unix_time", 
    average_cpu_usage = ["integer", 20, 30]
}

anomaly_data_config = {
    "data_trend": "AverageTrend",
    "feature" : "average_cpu_usage",
    "anomaly_percentage" : 0.001, 
    "avg_min" : 20, 
    "avg_max" : 30,
    "abs_min" : 0, 
    "abs_max" : 100
}
```

In the example above, `data_template` contains the document template to be generated: a document containing the timestamp and the `average_cpu_usage`. `anomaly_data_config` contains the config variables necessary to generate a `AverageTrend` trend with `average_cpu_usage` that ranged from [20, 30], inclusive. This trend had a 0.001 chance of generating an anomaly, which is a value outside [20, 30] with a range from [0, 100], inclusive.

For visual learners, if plotted on a time graph, it looks something like this (where anomalies are *):

```
100             Average CPU Usage




                 *

                 

30                           *
        --------- ------- --- ------
20

                         *
0
```

While the data trend only supports a straight-line average trend such as the example above, there is support for users to define their own functions. `AverageTrend` for example is a class that implements the abstract class `DataTrend`. If other users wanted to generate a tangent trend function, for instance, they might create a new class `TangentTrend` from `DataTrend`. 

To see more, visit `sample_data_plugins/ad_plugin_data_config/README.md` for more info.

### Customizing Trend Functions (for Anomaly Detection)

`DataTrend` is a class defined in `sample_data_plugins/ad_plugin_data_config/data_trend_interface.py`. 

`DataTrend` takes in three arguments for initialization:
- `feature` (string): The name of the field to generate a data trend
- `timestamp` (string): The *name* of the field which contains timestamps (in `unix time`)
- `current_date` (datetime): The date at which documents are generated (e.g. if the date was today, then documents will be generated with timestamp fields containing today's date in `unix time` milliseconds).

`DataTrend` also has two undefined functions:
- `generate_noise()`: Function that would mutate an existing document value so that an anomaly may be generated
- `generate_data_trend()`: Function that would mutate an existing the value of `feature` field to fit a user-defined trend

Keep in mind that `DataTrend` is designed such that it *does not generate documents*. Rather it's designed such that the values of existing documents will be changed to fit a trend. This means that `DataTrend` methods should return a single changed document, not newly generated documents. 

Thus, to generate a trend, one possible idea would be to pass in some sort of `delta` argument (not defined in `DataTrend`), which adds the `delta` between a previously generated value and a new one. For example, consider the linear regression `y = 7x`. To generate such a regression, having the `delta` argument set to 7 times the previous value would generate the line. To add some noise to the line, there could be another argument `margin`, which would make each new value `+- margin`, resulting in a trend, but not a perfect line.