"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from datetime import datetime
import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from sample_data_plugins.ad_plugin_data_config.data_trend_interface import DataTrend


# Test that initialization happens correctly
def test_valid_DataTrend():
    test_date = datetime.now()
    new_trend = DataTrend("test-feature", "unix", test_date)
    new_trend.generate_data_trend()
    new_trend.generate_noise()


# Test for bad input
def test_invalid_DataTrend():
    test_date = datetime.now()
    with pytest.raises(TypeError):
        bad_trend = DataTrend(["bad-test"], "unix", test_date)
    with pytest.raises(TypeError):
        bad_trend = DataTrend("bad-test", 1659040192, test_date)
    with pytest.raises(TypeError):
        bad_trend = DataTrend("bad-test", "unix", 1659040192)