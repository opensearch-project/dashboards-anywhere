# opensearch-py==2.0.0
from opensearchpy import OpenSearch

# Standard libraries
from json import loads, load
import pytest
import sys
import os

# Adds the directory "/sample_data_ingestion" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sample_data_ingestor import ingest

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

jinput = valid_test_inputs["jinput"]

jinput2 = valid_test_inputs["jinput2"]

jinput3 = valid_test_inputs["jinput3"]

jinput4 = valid_test_inputs["jinput4"]

jinput5 = valid_test_inputs["jinput5"]

jinput6 = valid_test_inputs["jinput6"]


# Sample index for testing 
if not client.indices.exists(index = INDEX_NAME):
    client.indices.create(index = INDEX_NAME, body = INDEX_BODY)


def test_valid_ingest():
    # Tests for minimum required arguments
    assert len(ingest(client, template = jinput, mapping = False, index_name = INDEX_NAME)) == 6
    assert len(ingest(client, template = jinput2, index_name = INDEX_NAME)) == 6
    path = str(DIR_PATH + "/test-files/csv-format-test-zipped.csv.gz")
    assert len(ingest(client, template = path, index_name = INDEX_NAME)) == 12
    path = str(DIR_PATH + "/test-files/ecommerce.json")
    assert len(ingest(client, file_provided = True, template = path, index_name = INDEX_NAME)) == 50

    # Tests for various arguments
    assert len(ingest(client, template = jinput3, mapping = False, index_name = INDEX_NAME, number = 8)) == 8
    
    # Test for trending data
    trend_test = ingest(client = client, template = jinput6, mapping = False, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", avg_min = 20, avg_max = 30, feature = "average cpu usage", abs_min = 0, abs_max = 200, anomaly_percentage = 0.3)
    assert len(trend_test) == 120
    count = 0
    for entry in trend_test:
        entry = loads(entry)
        if entry["average cpu usage"] > 30:
             count += 1
    assert (count/len(trend_test)) < 0.5


def test_invalid_ingest():
    # Testing missing required arguments
    with pytest.raises(TypeError):
        ingest(mapping = False, index_name = INDEX_NAME)
    # Testing bad arguments
    with pytest.raises(ValueError):
        ingest(client = client, template = jinput6, mapping = False, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", avg_min = 20, avg_max = -1, feature = "average cpu usage", abs_min = 0, abs_max = 200, anomaly_percentage = 0.3)    
    with pytest.raises(TypeError):
        ingest(client = client, template = jinput6, mapping = True, index_name = INDEX_NAME, number = 120, chunk = 10, timestamp = "date", avg_min = 20, avg_max = 30, feature = "average cpu usage", abs_min = 0, abs_max = 200, anomaly_percentage = 0.3)


# Deletes test index
if client.indices.exists(index = INDEX_NAME):
    client.indices.delete(index = INDEX_NAME)