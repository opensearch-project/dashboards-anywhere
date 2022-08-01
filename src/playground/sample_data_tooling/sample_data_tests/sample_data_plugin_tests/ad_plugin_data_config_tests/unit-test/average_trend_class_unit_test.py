from datetime import datetime
from json import dumps
import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from sample_data_plugins.ad_plugin_data_config.average_trend_class import AverageTrend


# Test that all functions function properly
def test_valid_AverageTrend():
    test_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    unix_time = int(test_date.strftime("%s")) * 1000
    test_entry = dumps({"timestamp": unix_time, "average_price": 547.19, "average_percent_off": 4})
    avg_percent_config = {
        "feature": "average_percent_off",
        "avg_min": 0,
        "avg_max": 10,
        "abs_min": 0,
        "abs_max": 100,
        "anomaly_percentage": 0,
    }
    new_avg = AverageTrend("timestamp", avg_percent_config, test_entry, test_date)
    assert new_avg.generate_data_trend() == test_entry
    avg_percent_config["anomaly_percentage"] = 1
    new_avg = AverageTrend("timestamp", avg_percent_config, test_entry, test_date)
    assert new_avg.generate_data_trend() != test_entry
    avg_price_config = {
        "feature": "average_price",
        "avg_min": 200,
        "avg_max": 4000,
        "abs_min": 0,
        "abs_max": 10000,
        "anomaly_percentage": 0,
    }
    new_avg = AverageTrend("timestamp", avg_price_config, test_entry, test_date)
    assert new_avg.generate_data_trend() == test_entry
    avg_price_config["anomaly_percentage"] = 1
    new_avg = AverageTrend("timestamp", avg_price_config, test_entry, test_date)
    assert new_avg.generate_data_trend() != test_entry


# Tests of bad input
def test_invalid_AverageTrend():
    test_date = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    unix_time = int(test_date.strftime("%s")) * 1000
    test_entry = dumps({"timestamp": unix_time, "average_price": 547.19, "average_percent_off": 4})
    avg_percent_config = {
        "feature": "average_percent_off",
        "avg_min": 40,
        "avg_max": 10,
        "abs_min": 0,
        "abs_max": 100,
        "anomaly_percentage": 0,
    }

    with pytest.raises(ValueError):
        new_avg = AverageTrend("timestamp", avg_percent_config, test_entry, test_date)
    avg_percent_config["avg_min"] = 0
    avg_percent_config["anomaly_percentage"] = 1.1
    with pytest.raises(ValueError):
        new_avg = AverageTrend("timestamp", avg_percent_config, test_entry, test_date)
    avg_percent_config["anomaly_percentage"] = 0
    with pytest.raises(ValueError):
        new_avg = AverageTrend("timestamp", avg_percent_config, "test_entry", test_date)
    avg_percent_config["avg_min"] = "1"
    with pytest.raises(TypeError):
        new_avg = AverageTrend("timestamp", avg_percent_config, test_entry, test_date)
    with pytest.raises(KeyError):
        new_avg = AverageTrend("timestamp", {}, test_entry, test_date)