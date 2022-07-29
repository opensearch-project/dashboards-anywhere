"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch
from json import load
import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_indices.sample_data_indices import SampleDataIndex


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

# Sample inputs (valid)
valid_test_inputs = {}
with open(DIR_PATH + "/test-files/valid-template-inputs.json", "r") as f:
    valid_test_inputs = load(f)

valid_json_shorthand = valid_test_inputs["valid_json_shorthand"]

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

# OpenSearch client object that will mock API calls
client = OpenSearch(transport_class = DummyTransport)


# Test that all functions operate properly without exceptions
def test_valid_Index():
    new_index = SampleDataIndex(INDEX_NAME, INDEX_BODY, client)
    new_index.create_index()
    new_index.delete_index()
    new_index.ingest_more(data_template = valid_json_shorthand, mapping = False, index_name = INDEX_NAME)


# Test that input validation works as intended
def test_invalid_Index():
    # Bad index_name argument
    with pytest.raises(TypeError):
        bad_index = SampleDataIndex(5, {}, client)
        bad_index.create_index()

    # Bad client argument
    with pytest.raises(TypeError):
        bad_index = SampleDataIndex("name", {}, "client")
        bad_index.delete_index()

    # Bad index_body argument
    with pytest.raises(TypeError):
        bad_index = SampleDataIndex("name", "body", client)
        bad_index.delete_index()

    # Bad ingest_more argument
    with pytest.raises(TypeError):
        bad_index = SampleDataIndex(INDEX_NAME, INDEX_BODY, client)
        bad_index.ingest_more()