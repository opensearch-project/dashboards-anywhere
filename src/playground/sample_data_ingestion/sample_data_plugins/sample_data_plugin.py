from datetime import datetime, timedelta
from os import environ, path, remove
from json import dumps, load, loads
from shutil import copyfileobj
from requests import request
from base64 import b64encode
from time import mktime
import gzip


"""
Generic Plugin class: initialization is defined here
Arguments:
    - index_name: The name of the source index
    - payload: The JSON body of which to call create API requests
    - base_url: The IP address/url where the OpenSearch backend lies
"""
class Plugin:
    def __init__(self, index_name, payload, base_url):
        self.index_name = index_name
        self.id = ""
        self.payload = payload
        
        # Convert to JSON string if necessary
        if type(self.payload) is dict:
            self.payload = dumps(self.payload)
        
        # Add authentication headers
        __auth_plain = environ.get("SAMPLE_DATA_USERNAME") + ":" + environ.get("SAMPLE_DATA_PASSWORD")
        __auth = b64encode(__auth_plain.encode("ascii"))
        __authorization = "Basic " + str(__auth).split("\'")[1]
        self.headers = {
            'Authorization': __authorization,
            'Content-Type': 'application/json'
        }

        # Build url
        self.base_url = base_url
        if self.base_url.endswith("/"):
          self.base_url = self.base_url[:-1]
        self.url = self.base_url + ":9200/"
    
    # If payload is a zipped config file, unzip it and return unzipped filename
    def unzip(self):
        if type(self.payload) is not str or (type(self.payload) is str and ".json" not in self.payload):
            print("Payload is not a filename or is not a .json file")
            return None
        if type(self.payload) is str and ".gz" not in self.payload:
            print("Payload is already unzipped")
            return self.payload
        with gzip.open(self.payload, 'rt') as fin:
            with open(self.payload.split(".gz")[0], 'wb') as fout:
                copyfileobj(fin, fout)
        return self.payload.split(".gz")[0]

    # Utility function to convert payload to a dict
    def convert_payload(self, payload, plugin_config_directory_name):
        if type(payload) is str and ".json" not in payload:
            payload = loads(payload)

        # If payload is a config file, navigate to the config file and load contents to payload (unzip if necessary)
        if type(self.payload) is str and ".json" in self.payload:
            dir_path = path.dirname(path.realpath(__file__))
            dir_path = dir_path.split("/sample_data_plugin")[0]
            config_file = self.unzip()
            dir_path += "/config/" + plugin_config_directory_name + "/" + config_file
            with open (dir_path, "r") as f:
                payload = load(f)

            # If the file was previously unzipped, remove the unzipped file
            if config_file != self.payload:
                remove(config_file)

        return payload


"""
AnomalyDetection class: Inherited class from Plugin class
Arguments (only for AnomalyDetection):
    - target_index: the index to store anomaly detector results
    - days_ago: how far back the historical analysis will start (default = 7 days)
"""
class AnomalyDetection(Plugin):
    def __init__(self, index_name, payload, base_url, target_index = None, days_ago = 7):
        super().__init__(index_name, payload, base_url)
        self.url += "_plugins/_anomaly_detection/"
        self.target_index = target_index
        self.days_ago = days_ago
    
    # Creates detector using the initial arguments
    def create_detector(self):
        payload = self.convert_payload(self.payload, "ad_plugin")
        endpoint = self.url + "detectors"
        payload["indices"] = self.index_name
        
        # Convert indices to an array type
        if type(self.index_name) is str:
            payload["indices"] = [self.index_name]
        
        # Modify payload and send API call
        if self.target_index:
            payload["result_index"] = self.target_index
        payload = dumps(payload)
        response = request("POST", endpoint, headers = self.headers, data = payload, verify = False)
        print(response.text)
        
        try:
            # Finds the id of the detector that was just created
            self.id = response.json()["_id"]
        except Exception as e:
            print(e)
            raise ValueError("Anomaly detection has improper configurations or already exists. Review the payload contents.")

    # Deletes detector; detector must already exist
    def delete_detector(self):
        endpoint = self.url + "detectors/" + self.id
        response = request("DELETE", endpoint, headers = self.headers, verify = False)
        print(response.text)

    # Starts the detector job (for historical analysis, set historical_analysis to True)
    def start_detector(self, historical_analysis = False):
        endpoint = self.url + "detectors/" + self.id + "/_start"
        if historical_analysis:
            start_range = datetime.today() - timedelta(days = self.days_ago)
            start_range = int(mktime(start_range.timetuple()) * 1000)
            end_range = datetime.today()
            end_range = int(mktime(end_range.timetuple()) * 1000)
            payload = {
                "start_time": start_range,
                "end_time": end_range
            }
            payload = dumps(payload)
            response = request("POST", endpoint, headers = self.headers, data = payload, verify = False)
            print(response.text)
        else:
            response = request("POST", endpoint, headers = self.headers, verify = False)
            print(response.text)

    # Stops the detector job (for historical analysis, set historical_analysis to True)
    def stop_detector(self, historical_analysis = False):
        endpoint = self.url + "detectors/" + self.id + "/_stop"
        if historical_analysis:
            endpoint += "?historical=true"
        response = request("POST", endpoint, headers = self.headers, verify = False)
        print(response.text)