import pytest
import sys
import os

# Adds the directory "/sample_data_tooling" to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sample_data_plugins.ad_plugin_class import AnomalyDetection
from sample_data_authentication.sample_data_basic_authentication import BasicAuthentication


# Constants
SAMPLE_FILE_PATH_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Tests that all functions work correctly
def test_valid_AnomalyDetection(requests_mock):
    sample_file_path = os.path.join(SAMPLE_FILE_PATH_DIRECTORY, "test-files/sample_data_ad_payload.json")
    new_auth = BasicAuthentication("admin", "admin")
    new_ad_plugin = AnomalyDetection("test_index", sample_file_path, "https://localhost", new_auth)
    assert new_ad_plugin.url == "https://localhost:9200/_plugins/_anomaly_detection/"
    
    # What sample mock requests would look like
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors", json = {"_id": "111", "response": "detector created"})
    requests_mock.delete("https://localhost:9200/_plugins/_anomaly_detection/detectors/111", json = {"response": "detector deleted"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_start", json = {"response": "detector job started"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop", json = {"response": "detector job stopped"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop?historical=true", json = {"response": "historical analysis job started"})

    # Calling every possible request
    assert new_ad_plugin.create_detector() == {"_id": "111", "response": "detector created"}
    assert new_ad_plugin.id == "111"
    assert new_ad_plugin.start_detector() == {"response": "detector job started"}
    assert new_ad_plugin.start_detector(True) == {"response": "detector job started"}
    assert new_ad_plugin.stop_detector() == {"response": "detector job stopped"}
    assert new_ad_plugin.stop_detector(True) == {"response": "historical analysis job started"}
    assert new_ad_plugin.delete_detector() == {"response": "detector deleted"}

# Tests that all exceptions are raised and input is all validated
def test_invalid_AnomalyDetection(requests_mock):
    sample_file_path = os.path.join(SAMPLE_FILE_PATH_DIRECTORY, "test-files/sample_data_ad_payload.json")
    new_auth = BasicAuthentication("admin", "admin")
    
    # Testing bad inputs (for arguments specific to AnomalyDetection)
    with pytest.raises(TypeError):
        bad_ad_plugin = AnomalyDetection("bad-index", sample_file_path, "https://localhost", new_auth, target_index=["BAD"])
    with pytest.raises(TypeError):
        bad_ad_plugin = AnomalyDetection("bad-index", sample_file_path, "https://localhost", new_auth, days_ago = 3.1)

    # Testing bad request calls
    bad_ad_plugin = AnomalyDetection("test_index", sample_file_path, "https://localhost", new_auth)
    
    # What sample mock requests would look like
    # Assume the detector with id "111" already exists
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors", json = {"error": "detector already exists"})
    requests_mock.delete("https://localhost:9200/_plugins/_anomaly_detection/detectors/111", json = {"response": "detector deleted"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_start", json = {"response": "detector job started"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop", json = {"response": "detector job stopped"})
    requests_mock.post("https://localhost:9200/_plugins/_anomaly_detection/detectors/111/_stop?historical=true", json = {"response": "historical analysis job started"})

    # If the plugin job was started, stopped, or the plugin was deleted before being created
    with pytest.raises(ValueError):
        assert bad_ad_plugin.delete_detector()
    with pytest.raises(ValueError):
        assert bad_ad_plugin.start_detector()
    with pytest.raises(ValueError):
        assert bad_ad_plugin.start_detector(True)
    with pytest.raises(ValueError):
        assert bad_ad_plugin.stop_detector()
    with pytest.raises(ValueError):
        assert bad_ad_plugin.stop_detector(True)

    # Tests for the detector already existing
    with pytest.raises(ValueError):
        assert bad_ad_plugin.create_detector() == {"error": "detector already exists"}