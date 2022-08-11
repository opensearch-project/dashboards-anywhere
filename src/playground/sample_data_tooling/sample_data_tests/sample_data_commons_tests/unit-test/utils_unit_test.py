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
from sample_data_tooling.sample_data_commons.utils import validate_filename, unzip_file, validate_job_args, untar_file
from sample_data_tooling.sample_data_authentication.sample_data_basic_authentication import BasicAuthentication


# Constants
DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Tests that all types are supported (zipped or unzipped)
def test_valid_validate_filename():
    validate_filename("a.csv.gz")
    validate_filename("b.json.gz")
    validate_filename("js.ndjson")


# Tests of input validation
def test_invalid_validate_filename():
    with pytest.raises(TypeError):
        validate_filename(1)
    with pytest.raises(ValueError):
        validate_filename("a.pdf")
    with pytest.raises(ValueError):
        validate_filename("json.pdf")
    with pytest.raises(ValueError):
        validate_filename("csv.jso")


# Tests that all correct filetypes are read
def test_unzip_file():
    assert unzip_file(DIR_PATH + "/test-files/example_config_ndjson.ndjson") == None
    assert unzip_file(DIR_PATH + "/test-files/example_config_json.json") == DIR_PATH + "/test-files/example_config_json.json"
    assert unzip_file(DIR_PATH + "/test-files/example_config_json_zipped.json.gz") == DIR_PATH + "/test-files/example_config_json_zipped.json"
    assert unzip_file(DIR_PATH + "/test-files/sample_file_ignore.txt") == None
    assert unzip_file(457423) == None
    os.remove(DIR_PATH + "/test-files/example_config_json_zipped.json")


# Tests that no errors would be raised for each argument
def test_valid_validate_job_args():
    example_header = BasicAuthentication("u", "p")
    client = OpenSearch()
    validate_job_args("some/path", "https://example", example_header, client)


# Tests bad inputs
def test_invalid_validate_job_args():
    example_header = BasicAuthentication("u", "p")
    client = OpenSearch()
    with pytest.raises(TypeError):
        validate_job_args({"key": "value"}, "https://example", example_header, client)
    with pytest.raises(TypeError):
        validate_job_args("bad/path", ["https://example"], example_header, client)
    with pytest.raises(TypeError):
        validate_job_args("some/path", "https://example", {"example_header": True}, client)
    with pytest.raises(TypeError):
        validate_job_args("some/path", "https://example", example_header, 142)


# Test that only tar.gz files are extracted
def test_untar_file():
    assert untar_file(DIR_PATH + "/test-files/example_config_ndjson.ndjson") == []
    assert untar_file(DIR_PATH + "/test-files/example_config_json.json") == []
    assert untar_file(DIR_PATH + "/test-files/example_config_json_zipped.json.gz") == []
    assert untar_file(DIR_PATH + "/test-files/example_tarfile.tar.gz", os.path.join(DIR_PATH, "test-files")) == [os.path.join(DIR_PATH, "test-files", "tarfile.txt"), os.path.join(DIR_PATH, "test-files", "tarfile_two.txt")]
    os.remove(os.path.join(DIR_PATH, "test-files", "tarfile.txt"))
    os.remove(os.path.join(DIR_PATH, "test-files", "tarfile_two.txt"))
