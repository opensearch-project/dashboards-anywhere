from opensearchpy import OpenSearch

# Standard libraries
from json import loads, load
import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_ingestor.sample_data_ingestor import ingest, build_request_body

# Constants
INDEX_NAME = "ingest-test"
DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
INDEX_BODY = {
  'settings': {
    'index': {
      'number_of_shards': 1
    }
  }
}


# Configurations for connection (NEED TO CHANGE)
HOST = os.environ.get("HOST")
PORT = 9200
AUTH = (os.environ.get("SAMPLE_DATA_USERNAME"), os.environ.get("SAMPLE_DATA_PASSWORD"))


# Establish connection with OS
client = OpenSearch(
    hosts = [{'host': HOST, 'port': PORT}],
    http_compress = True,
    http_auth = AUTH,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)


# Sample inputs (valid)
valid_test_inputs = {}
with open(DIR_PATH + "/test-files/valid-template-inputs.json", "r") as f:
    valid_test_inputs = load(f)

valid_json_shorthand = valid_test_inputs["valid_json_shorthand"]

valid_json_mapping = valid_test_inputs["valid_json_mapping"]

valid_json_array_shorthand = valid_test_inputs["valid_json_array_shorthand"]

valid_json_array_mapping = valid_test_inputs["valid_json_array_mapping"]

valid_json_array_mapping_args = valid_test_inputs["valid_json_array_mapping_args"]

valid_json_shorthand_data_trend = valid_test_inputs["valid_json_shorthand_data_trend"]


# Sample index for testing 
if not client.indices.exists(index = INDEX_NAME):
    client.indices.create(index = INDEX_NAME, body = INDEX_BODY)


def test_valid_ingest():
    # Tests for minimum required arguments
    assert len(ingest(client, data_template = valid_json_shorthand, mapping = False, index_name = INDEX_NAME)) == 6
    assert len(ingest(client, data_template = valid_json_mapping, index_name = INDEX_NAME)) == 6
    path = str(DIR_PATH + "/test-files/csv-format-test-zipped.csv.gz")
    assert len(ingest(client, data_template = path, index_name = INDEX_NAME)) == 12
    path = str(DIR_PATH + "/test-files/ecommerce.json")
    assert len(ingest(client, file_provided = True, data_template = path, index_name = INDEX_NAME)) == 50

    # Tests for various arguments
    assert len(ingest(client, data_template = valid_json_array_shorthand, mapping = False, index_name = INDEX_NAME, number = 8)) == 8
    
    # Test for trending data
    anomaly_detection_trend =  [{
            "data_trend": "AverageTrend",
            "feature" : "average cpu usage",
            "anomaly_percentage" : 0.001, 
            "avg_min" : 20, 
            "avg_max" : 30,
            "abs_min" : 0, 
            "abs_max" : 100
        }]
    trend_test = ingest(client = client, data_template = valid_json_shorthand_data_trend, mapping = False, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", anomaly_detection_trend = anomaly_detection_trend)
    assert len(trend_test) == 120
    count = 0
    for entry in trend_test:
        entry = loads(entry)
        if entry["average cpu usage"] > 30:
             count += 1
    assert (count/len(trend_test)) < 0.5

def test_build_request_body():
    dataset = []
    with open(DIR_PATH + "/test-files/ecommerce.json", "r") as f:
        for line in f:
            dataset.append(line)
    assert len(build_request_body(index_name = "test", file_provided = False, timestamp = None, minutes = 0, chunk = 5, chunk_index = 0, current_index = 0, dataset = dataset, max_bulk_size = 100)[0]) < 10
    assert len(build_request_body(index_name = "test", file_provided = False, timestamp = None, minutes = 0, chunk = 5, chunk_index = 0, current_index = 0, dataset = dataset, max_bulk_size = 100000000)[0]) == 10


def test_invalid_ingest():
    # Testing missing required arguments
    with pytest.raises(TypeError):
        ingest(mapping = False, index_name = INDEX_NAME)
    # Testing bad arguments
    anomaly_detection_trend =  [{
            "data_trend": "AverageTrend",
            "feature" : "average cpu usage",
            "anomaly_percentage" : 0.001, 
            "avg_min" : 20, 
            "avg_max" : -1,
            "abs_min" : 0, 
            "abs_max" : 200
        }]
    with pytest.raises(ValueError):
        ingest(client = client, data_template = valid_json_shorthand_data_trend, mapping = False, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", anomaly_detection_trend = anomaly_detection_trend)
    with pytest.raises(TypeError):
        anomaly_detection_trend[0]["avg_max"] = 30
        ingest(client = client, data_template = valid_json_shorthand_data_trend, mapping = True, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", anomaly_detection_trend = anomaly_detection_trend)


# Deletes test index
if client.indices.exists(index = INDEX_NAME):
    client.indices.delete(index = INDEX_NAME)