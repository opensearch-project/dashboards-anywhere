"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from datetime import datetime, timedelta
from requests import request
from time import mktime
from json import dumps
from os import path
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_authentication.sample_data_authentication import Authentication
from sample_data_plugins.sample_data_plugin import Plugin


class AnomalyDetection(Plugin):
    """
    AnomalyDetection class: Inherited class from Plugin class

    Arguments (only for AnomalyDetection):
        - target_index: the index to store anomaly detector results
        - days_ago: how far back the historical analysis will start (default = 7 days)

    Raises:
        - TypeError: Invalid target_index: target_index is a string representing the index name to store results
        - TypeError: Invalid days_ago: days_ago is an integer representing how far back historical analysis should go
    """
    def __init__(self, index_name:str, payload, base_url:str, auth:Authentication, target_index:str = None, days_ago:int = 7):
        # Validate input
        if target_index and type(target_index) is not str:
            raise TypeError("Invalid target_index: target_index is a string representing the index name to store results")
        if type(days_ago) is not int:
            raise TypeError("Invalid days_ago: days_ago is an integer representing how far back historical analysis should go")

        super().__init__(index_name, payload, base_url, auth)
        self.url += "_plugins/_anomaly_detection/"
        self.target_index = target_index
        self.days_ago = days_ago

    def create_detector(self) -> dict:
        """
        Creates detector using the initial arguments

        Raises:
            - ConnectionError: Anomaly plugin failed to be created; check plugin and/or client configurations
            - ValueError: Anomaly detection has improper configurations or already exists. Review the payload contents.

        Returns:
            - The response as a JSON dict
        """

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
        try:
            response = request("POST", endpoint, headers = self.headers, data = payload, verify = False)
        except Exception as e:
            print(e)
            raise ConnectionError("Anomaly plugin failed to be created; check plugin and/or client configurations")

        # Sample response
        # {
        #     "_id": "VEHKTXwBwf_U8gjUXY2s",
        #     "_version": 1,
        #     "_seq_no": 5,
        #     "anomaly_detector": {"<configurations of the detector>"}
        # }
        print(response.text)

        try:
            # Finds the id of the detector that was just created
            self.id = response.json()["_id"]
        except Exception as e:
            print(e)
            raise ValueError("Anomaly detection has improper configurations or already exists. Review the payload contents.")

        return response.json()

    def delete_detector(self) -> dict:
        """
        Deletes detector; detector must already exist

        Raises:
            - ValueError: id is not defined; this is probably because deleting the ad plugin was called before it was created
            - ConnectionError: Anomaly plugin failed to be deleted; review the client configurations

        Returns:
            - The response as a JSON dict
        """

        # Input validation
        if not self.id:
            raise ValueError("id is not defined; this is probably because deleting the ad plugin was called before it was created")

        endpoint = self.url + "detectors/" + self.id
        try:
            response = request("DELETE", endpoint, headers = self.headers, verify = False)
        except Exception as e:
            print(e)
            raise ConnectionError("Anomaly plugin failed to be deleted; review the client configurations")

        # Sample response
        # {
        #     "_index": ".opensearch-anomaly-detectors",
        #     "_id": "70TxTXwBjd8s6RK4j1Pj",
        #     "_version": 2,
        #     "result": "deleted",
        #     "forced_refresh": true,
        #     "_shards": {
        #         "total": 2,
        #         "successful": 2,
        #         "failed": 0
        #     },
        #     "_seq_no": 9,
        #     "_primary_term": 1
        # }
        print(response.text)

        return response.json()

    def start_detector(self, historical_analysis:bool = False) -> dict:
        """
        Starts the detector job (for historical analysis, set historical_analysis to True)

        Arguments:
            - historical_analysis: whether or not the job starting is historical analysis or to start the detector

        Raises:
            - ValueError: id is not defined; this is probably because ad plugin was not created yet before calling start_detector()
            - TypeError: Invalid historical_analysis: historical_analysis is a boolean value
            - ConnectionError: Anomaly plugin historical analysis job failed to start; check the argument days_ago or review the client configurations
            - ConnectionError: Anomaly plugin detector job failed to start; check the client configurations

        Returns:
            - The response as a JSON dict
        """

        # Input validation
        if not self.id:
            raise ValueError("id is not defined; this is probably because ad plugin was not created yet before calling start_detector()")
        if type(historical_analysis) is not bool:
            raise TypeError("Invalid historical_analysis: historical_analysis is a boolean value")

        endpoint = self.url + "detectors/" + self.id + "/_start"
        if historical_analysis:
            # Creating the payload necessary to start historical analysis within a range
            start_range = datetime.today() - timedelta(days = self.days_ago)
            start_range = int(mktime(start_range.timetuple()) * 1000)
            end_range = datetime.today()
            end_range = int(mktime(end_range.timetuple()) * 1000)
            payload = {
                "start_time": start_range,
                "end_time": end_range
            }
            payload = dumps(payload)
            try:
                response = request("POST", endpoint, headers = self.headers, data = payload, verify = False)
            except Exception as e:
                print(e)
                raise ConnectionError("Anomaly plugin historical analysis job failed to start; check the argument days_ago or review the client configurations")
            print(response.text)
        else:
            try:
                response = request("POST", endpoint, headers = self.headers, verify = False)
            except Exception as e:
                print(e)
                raise ConnectionError("Anomaly plugin detector job failed to start; check the client configurations")

            # Sample response
            # {
            #     "_id": "f9DsTXwB6HknB84SoRTY",
            #     "_version": 1,
            #     "_seq_no": 958,
            #     "_primary_term": 1
            # }
            print(response.text)

        return response.json()

    def stop_detector(self, historical_analysis:bool = False) -> dict:
        """
        Stops the detector job (for historical analysis, set historical_analysis to True)

        Arguments:
            - historical_analysis: whether or not the job stopping is historical analysis or the detector

        Raises:
            - ValueError: id is not defined; this is probably because ad plugin was not created yet before calling stop_detector()
            - TypeError: Invalid historical_analysis: historical_analysis is a boolean value
            - ConnectionError: Anomaly plugin detector job failed to stop; check the client configurations

        Returns:
            - The response as a JSON dict
        """

        # Input validation
        if not self.id:
            raise ValueError("id is not defined; this is probably because ad plugin was not created yet before calling stop_detector()")
        if type(historical_analysis) is not bool:
            raise TypeError("Invalid historical_analysis: historical_analysis is a boolean value")

        endpoint = self.url + "detectors/" + self.id + "/_stop"
        if historical_analysis:
            endpoint += "?historical=true"
        try:
            response = request("POST", endpoint, headers = self.headers, verify = False)
        except Exception as e:
            print(e)
            raise ConnectionError("Anomaly plugin detector job failed to stop; check the client configurations")

        # Sample response
        # {
        #     "_id": "f9DsTXwB6HknB84SoRTY",
        #     "_version": 0,
        #     "_seq_no": 0,
        #     "_primary_term": 0
        # }
        print(response.text)

        return response.json()