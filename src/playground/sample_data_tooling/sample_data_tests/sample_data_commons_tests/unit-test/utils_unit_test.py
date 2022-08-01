from opensearchpy import OpenSearch

# Standard libraries
import pytest
import sys
import os


# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_commons.utils import validate_filename, unzip_file


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
