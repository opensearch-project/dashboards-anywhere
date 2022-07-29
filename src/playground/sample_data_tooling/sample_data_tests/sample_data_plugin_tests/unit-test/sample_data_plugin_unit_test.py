"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_plugins.sample_data_plugin import Plugin
from sample_data_authentication.sample_data_basic_authentication import BasicAuthentication


# Constants
SAMPLE_FILE_PATH_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Tests that all functions work correctly
def test_valid_Plugin():
    sample_file_path = os.path.join(SAMPLE_FILE_PATH_DIRECTORY, "test-files/sample_data_payload.json")
    new_auth = BasicAuthentication("admin", "admin")
    new_plugin = Plugin("test_index", sample_file_path, "https://localhost", new_auth)
    assert new_plugin.url == "https://localhost:9200/"
    assert new_plugin.unzip() == sample_file_path
    assert new_plugin.convert_payload(sample_file_path, sample_file_path) == {"key": "value"}
    assert new_plugin.convert_payload({"key": "value"}, sample_file_path) == {"key": "value"}
    assert new_plugin.convert_payload('{"key": "value"}', sample_file_path) == {"key": "value"}


# Tests that all exceptions are raised and input is all validated
def test_invalid_Plugin():
    sample_file_path = os.path.join(SAMPLE_FILE_PATH_DIRECTORY, "test-files/sample_data_payload.json")
    new_auth = BasicAuthentication("admin", "admin")

    # Bad arguments
    with pytest.raises(TypeError):
        bad_plugin = Plugin({"bad": "index"}, sample_file_path, "https:localhost/", new_auth)
        bad_plugin.unzip()
    with pytest.raises(ValueError):
        bad_plugin = Plugin("bad-index", "somefile.pdf", "https:localhost/", new_auth)
        bad_plugin.unzip()
    with pytest.raises(TypeError):
        bad_plugin = Plugin("bad-index", sample_file_path, 24, new_auth)
        bad_plugin.unzip()
    with pytest.raises(TypeError):
        bad_plugin = Plugin("bad-index", sample_file_path,  "https:localhost/", ["auth"])
        bad_plugin.unzip()

    # Bad arguments for convert_payload()
    with pytest.raises(TypeError):
        bad_plugin = Plugin("test_index", sample_file_path, "https://localhost", new_auth)
        bad_plugin.convert_payload(sample_file_path, 4)
    with pytest.raises(TypeError):
        bad_plugin = Plugin("test_index", "sample_file_path", "https://localhost", new_auth)
        bad_plugin.convert_payload("sample_file_path", sample_file_path)
    with pytest.raises(TypeError):
        bad_plugin = Plugin("test_index", sample_file_path, "https://localhost", new_auth)
        bad_plugin.convert_payload(32462, sample_file_path)