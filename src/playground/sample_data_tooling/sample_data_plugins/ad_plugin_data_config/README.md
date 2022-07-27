# Generating Data For Anomaly Detection

For users who want trends with outliers in their data and not completely random data, then this tool provides support in the form of `DataTrend` class.

## Data Trend 

`DataTrend` is the abstract class used to define the basic structure of generating trends. Keep in mind that `DataTrend` is designed such that it *does not generate documents*. Rather it's designed such that the values of existing documents will be changed to fit a trend with some anomalies. This means that `DataTrend` methods should have a single existing document and return a single changed document, not newly generated documents. 

It is also assumed that data trends are for time series data, as this is what the anomaly detection plugin supports. This is why `current_date` (see below) is a required argument. Additionally, `DataTrend` was designed for numeric based anomalies.

`DataTrend` takes in three arguments for initialization:
- `feature` (string): The name of the field to generate a data trend
- `timestamp` (string): The *name* of the field which contains timestamps (in `unix time`)
- `current_date` (datetime): The date at which documents are generated (e.g. if the date was today, then documents will be generated with timestamp fields containing today's date in `unix time` milliseconds). `DataTrend` does not convert to `unix_time` so the functions below should convert to `unix_time` (milliseconds)

`DataTrend` also has two undefined functions:
- `generate_noise()`: Function that would mutate an existing document value so that an anomaly may be generated. The idea with this function is that it produces some outliers, which is configurable by setting some sort of percentage (like `AverageTrend` class and the `anomaly_percentage` argument).
- `generate_data_trend()`: Function that would mutate an existing the value of `feature` field to fit a user-defined trend. The idea with this function is that every document that is passed in will output the same document but with its "feature" having a changed numeric value to fit the trend.

## Average Trend (implements from Data Trend)

`AverageTrend` is the only current implementation of `DataTrend`. `AverageTrend` generates a straight-line trend with some anomalies (see below for visual representation).

```
                 *

                 

                             *
   -------------- ------- --- ---------------------------- --------------------

                                                          *
                         *
```

In addition to the arguments from `DataTrend`, `AverageTrend` takes two arguments:
- `feature_trend` (dict): This is the configurations specific to `AverageTrend`. Below are the required keys.
    - `"data_trend"` (string): While `AverageTrend` will not use this key, this is needed for when the ingestion tool determines which data trend to generate.
    - `"feature"` (string): The name of the field to generate a data trend. This is what will be passed into `DataTrend` `__init__`. 
    - `"avg_min"` (integer, float): The minimum value range for generating data within the trend
    - `"avg_max"` (integer, float): The maximum value range for generating data within the trend
    - `"abs_min"` (integer, float): The minimum value range for generating data outliers 
    - `"abs_max"` (integer, float): The maximum value range for generating data outliers
    - `"anomaly_percentage"` (float): The changes of an anomaly being generated (minimum 0.001, maximum: 1)
    - `"other_args"` (dict): This optional key is for any arguments when generating data anomalies. Typically, they should follow the existing arguments of the `data_template` (see `sample_data_generator/README.md` for more information on `data_template`). The only argument(s) that would change for the anomaly is the `min_value` and the `max_value`.
- `entry` (JSON string, list, dict): This is the existing document that will be mutated with trend data. `AverageTrend` will only return a list of JSON strings (if `entry` were a list) or a single JSON string (if `entry` were a JSON string or dict)

`AverageTrend` has two functions:
- `generate_noise()`: Given an initial value, either return initial value (representing no anomaly) or return a new value (representing the anomaly). This function should only be called by `generate_data_trend()`.
    - **Arguments:**
        - `initial_value` (integer, float): The initial value to change or remain the same
    - **Returns:**
        - This function returns an integer or float representing the final value to be put into the document
- `generate_data_trend()`: Given an existing document, return the newly modified document that simulates a straight-line trend.
    - **Returns:**
        - This function returns a list of new document(s) as a JSON string (if `entry` was a list) or a single document as a JSON string (if `entry` was a JSON string or dict)

## Defining Custom Data Trends

```
                             *                      *                            
                   *                  *                                     *
          *                                  *                          *
     *                                                               *
  *                                                             *
*                                                         *
```

`AverageTrend` might not be suited for all use cases for anomaly detection. After all, it is only one trend of many possible trend functions. This is why this tooling supports users to define their own custom data trends (functions is also another word but it can be quickly confused with class functions). `DataTrend` was designed to be overridden such that users can implement their own trends. 

Again, one detail to note is that this trend class should take in one existing document and return one modified document. Additionally, this custom trend should have an argument for a dictionary of trend-specific arguments, such as `AverageTrend`. One key that is necessary for this dictionary is the `"data_trend"` key as the ingestion tool uses this key to determine which trend class to call.

Thus, the major challenge to think about for implementing data trends using this class is how to generate trends when you only have access to one document per class call. 