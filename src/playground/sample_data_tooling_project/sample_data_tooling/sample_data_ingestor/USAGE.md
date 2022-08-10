## Example: Ingesting car auction data

For this example, we will continue to use the car auction data from the `sample_data_generator/USAGE.md`. As a primer, the data will contain car makes and models, the date of the auction, and the winning final bid price as a range between $20,000 and $40,000. However, to simulate a data trend, we modify `auction_date` to be the auctions that happened in a particular day, so this field becomes `unix_time`.

```
car_template = {
    "make": "vehicle_make",
    "model": "vehicle_model",
    "year": "vehicle_year",
    "auction_date": ["date_between", "-10y"],
    "final_winning_bid": ["float", {"right_digits": 2, "min_value": 20000, "max_value": 40000}]
}
```

This would be template to use. For the purposes of this example, the `index_name` might be named `"car_auction_data"`. Since `car_template` is a JSON "Short-hand" (again, see the `sample_data_generator/README.md` for more information), `mapping = False`. The `car_template` is data we want to generate, not read from, so `file_provided = False`. `chunk` can be any number but because we are only generating a day's worth of data, a good chunk size might be something easily divisible, like `chunk = 10`. The `timestamp = "auction_date"`. For the purposes of this example, we can assume `minutes = 30` as that could be the average amount of time an auction takes. Since `minutes` are defined, `number` should be the total amount of minutes per day divided by `minutes` or 1440/30 or `number = 48` (in my startup and refresh jobs, this is automatically configured). As for `current_date`, let's set the date to Jun 8, 2020 (which was the real launch date for a car auction website). As for `max_bulk_size`, which is the maximum request body byte size, let's leave it unchanged at 100000 bytes since we already defined `chunk`.

Finally, `anomaly_detection_trend` should have a list of payloads as we want to simulate a trend using `AverageTrend`. Now, to use `AverageTrend`, it requires the following arguments:
- `timestamp`: we defined this earlier so its still `"auction_date"`
- `feature_trend`: These are the configurations specific to `AverageTrend`:
    - `feature`: This is the field which we want to generate data trend. In our case, `feature = final_winning_bid`
    - `avg_min`: This should be $20000 (`avg_min = 20000`) as that is the average minimum winning bid price.
    - `avg_max`: Same logic as for `avg_min`; `avg_max = 40000`
    - `abs_min`: This is the absolute lowest a bid can go, which in this case is $0 (`abs_min = 0`)
    - `abs_max`: This is the absolute max a bid can go, which we cap the price off at say $150000 (`abs_max = 150000`)
    - `anomaly_percentage`: Lets assume the probability of an abnormal auction happening is 0.01. Thus, `anomaly_percentage = 0.01`
    - `other_args`: Because anomalies might generate the default arguments and we want a pricetag, let's set `other_args = {"right_digits": 2}`

`ingest()` after all these arguments looks as follows:

```
from sample_data_ingestor import ingest
from opensearchpy import OpenSearch
from datetime import datetime
from json import loads

# See OpenSearch Python client for reference on using the OpenSearch Python client object

# Dummy Serializer to make mock API calls
class DummySerializer():
    def dumps(self):
        return ""

# Transport class that makes a mock API call
class DummyTransport(object):
    def __init__(self, hosts, responses=None, **kwargs):
        self.serializer = DummySerializer
    def perform_request(self, method, url, params=None, headers=None, body=None):
        return None

# OpenSearch client object that will mock API calls
client = OpenSearch(transport_class = DummyTransport)

feature_trend = {
    "data_trend": "AverageTrend",
    "feature" : "final_winning_bid",
    "anomaly_percentage" : 0.01,
    "avg_min" : 20000,
    "avg_max" : 40000,
    "abs_min" : 0,
    "abs_max" : 150000,
    "other_args": {"right_digits": 2}
}

car_template = {
    "make": "vehicle_make",
    "model": "vehicle_model",
    "year": "vehicle_year",
    "auction_date": ["date_between", "-10y"],
    "final_winning_bid": ["float", {"right_digits": 2, "min_value": 20000, "max_value": 40000}]
}

# This variable is a list as documents can have multiple features
anomaly_detection_trend = [feature_trend]

result = ingest(
    client = client,
    data_template = car_template,
    index_name = "car_auction_data",
    file_provided = False,
    mapping = False,
    number = 48,
    chunk = 10,
    timestamp = "auction_date",
    minutes = 30,
    current_date = datetime(2020, 6, 8),
    anomaly_detection_trend = anomaly_detection_trend
)

# The entire list
print(result)

# Each pricetag generated
for doc in result:
    from json import loads
    doc_as_dict = loads(doc)
    print(doc_as_dict["final_winning_bid"])

<LIST PRINTED HERE>
<PRICES LISTED BELOW>
```

To spare the trouble of looking at many lines of output, there should be 48 document entries of JSON strings, with most of the `final_winning_bid` being between 20000 and 40000.
