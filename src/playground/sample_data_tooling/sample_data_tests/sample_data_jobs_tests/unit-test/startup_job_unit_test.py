"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch

# Standard libraries
import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_authentication.sample_data_basic_authentication import BasicAuthentication
from sample_data_jobs.startup_job import startup_job


# Serializer class that returns nothing; used to mock API call
class DummySerializer():
    def dumps(self):
        return ""

# Transport class that makes a mock API call
class DummyTransport(object):
    def __init__(self, hosts, responses=None, **kwargs):
        self.serializer = DummySerializer
    def perform_request(self, method, url, params=None, headers=None, body=None):
        return None


# Directory of current unit test file
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


# OpenSearch client object that will mock API calls
client = OpenSearch(transport_class = DummyTransport)
header = BasicAuthentication("admin", "admin")
config_path = os.path.join(os.path.dirname(DIR_PATH), "test-files")
url = "https://localhost"


# Testing that the startup job calls and does as expected without errors
def test_valid_startup_job(requests_mock):
    # All sample request calls
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors", json = {"_id": "111", "response": "detector created"})
    requests_mock.delete("https://localhost:9200/_plugins/_anomaly_detection/detectors/111", json = {"response": "detector deleted"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_start", json = {"response": "detector job started"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop", json = {"response": "detector job stopped"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop?historical=true", json = {"response": "historical analysis job started"})

    startup_job(config_path, url, header, client)


# Testing invalid inputs
def test_invalid_startup_job(requests_mock):
    # All sample request calls
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors", json = {"_id": "111", "response": "detector created"})
    requests_mock.delete("https://localhost:9200/_plugins/_anomaly_detection/detectors/111", json = {"response": "detector deleted"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_start", json = {"response": "detector job started"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop", json = {"response": "detector job stopped"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop?historical=true", json = {"response": "historical analysis job started"})

    with pytest.raises(TypeError):
        startup_job([config_path], url, header, client)
    with pytest.raises(TypeError):
        startup_job(config_path, 357, header, client)
    with pytest.raises(TypeError):
        startup_job(config_path, url, client, client)
    with pytest.raises(TypeError):
        startup_job(config_path, url, header, {"client": client})