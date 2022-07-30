import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_commons.utils import validate_filename


def test_valid_validate_filename():
    validate_filename("a.csv.gz")
    validate_filename("b.json.gz")
    validate_filename("js.ndjson")


def test_invalid_validate_filename():
    with pytest.raises(TypeError):
        validate_filename(1)
    with pytest.raises(ValueError):
        validate_filename("a.pdf")
    with pytest.raises(ValueError):
        validate_filename("json.pdf")
    with pytest.raises(ValueError):
        validate_filename("csv.jso")