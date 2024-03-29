"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

import pytest
import sys
import os

# Adds parent directory sample_data_tooling to sys.path
sys.path.append(os.path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.sample_data_authentication.sample_data_basic_authentication import BasicAuthentication


# Test that basic authentication works and returns as expected
def test_valid_BasicAuthentication():
    new_auth = BasicAuthentication("admin", "admin")
    assert new_auth.get_auth() == {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Content-Type': 'application/json'
    }


# Test of input validation
def test_invalid_BasicAuthentication():
    # Bad username argument
    with pytest.raises(TypeError):
        bad_auth = BasicAuthentication(1, "Bad")

    # Bad password argument
    with pytest.raises(TypeError):
        bad_auth = BasicAuthentication("Bad", {})
