# opensearch-py==2.0.0
from opensearchpy import OpenSearch

# Standard libraries
from json import dumps, loads
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sample_data_ingestor import ingest

# Constants
INDEX_NAME = "ingest-test"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
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
CA_CERTS_PATH = DIR_PATH.replace('utils/sample_data_ingestor/tests', '')
CA_CERTS_PATH += 'config/root-ca.pem'

# Establish connection with OS
client = OpenSearch(
    hosts = [{'host': HOST, 'port': PORT}],
    http_compress = True,
    http_auth = AUTH,
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
    ca_certs = CA_CERTS_PATH
)


# Sample inputs (valid)
jinput = {
        "year": "year",
        "random number": "integer",
        "email": "email",
        }

jinput2 = {"properties": {
        "first name":    { "type" : ["first_name"]},
        "last name":     { "type" : "last_name"},
        "companies":{ "type" : ["array", "company", 5] }
        }}

jinput3 = dumps({
        "year": "year",
        "addresses": ["array", "address", "integer", [1, 3]],
        "director": "name"
        })

jinput4 = dumps({"properties": {
        "year":    { "type" : ["year"]},
        "addresses":     { "type" : ["array", "address", "integer", (1, 3)] },
        "director":{ "type" : "name" }
        }})

jinput5 = dumps({"properties": {
        "year":    { "type" : ["year"]},
        "integers":     { "type" : ["array", "integer", "integer", (1, 3), 5, 10] },
        "director":{ "type" : "name" }
        }})

jinput6 = {
        "date": "unix_time",
        "average cpu usage": ["integer", 20, 30]
}


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