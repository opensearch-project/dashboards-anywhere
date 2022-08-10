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
sys.path.append(os.path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.sample_data_jobs.refresh_job import refresh_job


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
config_path = os.path.join(os.path.dirname(DIR_PATH), "test-files")


# Testing that the refresh job calls and does as expected without errors
def test_valid_refresh_job():
    refresh_job(config_path, client)


# Testing invalid inputs
def test_invalid_refresh_job():
    with pytest.raises(TypeError):
        refresh_job(123, client)
    with pytest.raises(TypeError):
        refresh_job(config_path, [client])
