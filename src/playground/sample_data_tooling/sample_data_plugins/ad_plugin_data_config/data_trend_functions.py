"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from datetime import datetime, timedelta
from json import loads, dumps
from random import randint
import sys
import os

# Adds the folder sample_data_tooling to the sys path
sys.path.append(os.path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.sample_data_plugins.ad_plugin_data_config.data_trend_interface import DataTrend
from sample_data_tooling.sample_data_generator.sample_data_generator import choose_field


class AverageTrend(DataTrend):
    """
    Class that generates values between a range and outliers

    Visual example:

                 *

                             *
        --------- ------- --- ------


                         *

    Arguments (only for AverageTrend):
        - feature_trend: A dict to use for generating a trend for a specific feature; required arguments
          are listed below:
            - avg_min: The lowest average value in which there is no anomaly
            - avg_max: The highest average value in which there is no anomaly
            - abs_min: The lowest possible value, which can be an anomaly
            - abs_max: The highest possible value, which can be an anomaly
            - anomaly_percentage: How often an anomaly occurs (minimum non-zero percentage: 0.001, maximum: 1)
            - other_args: Any other arguments required for the field with anomalies
        - entry: The document to have one of its field values potentially change

    Raises:
        - ValueError: Invalid values for number ranges
        - ValueError: Invalid anomaly percentage: it should be between 0 and 1, inclusive
        - TypeError: Invalid anomaly_detection_trend: anomaly_detection_trend should be a list, not a dict
        - ValueError: Invalid entry: if entry is a string, entry should only be a JSON string
        - TypeError: Invalid entry: entry should only be a string, list, or dict
        - ValueError: Invalid entry: entry is empty
        - TypeError: Invalid other_args: other_args should be a dict
    """
    def __init__(self,
        timestamp,
        feature_trend,
        entry,
        current_date = (datetime.today() - timedelta(days = 7))
    ):
        super().__init__(
            feature_trend["feature"],
            timestamp,
            current_date
        )
        # Unpacking values from anomaly_detection_trend
        self.avg_min = feature_trend["avg_min"]
        self.avg_max = feature_trend["avg_max"]
        self.abs_min = feature_trend["abs_min"]
        self.abs_max = feature_trend["abs_max"]
        self.anomaly_percentage = feature_trend["anomaly_percentage"]
        self.other_args = {}
        if "other_args" in feature_trend:
            self.other_args = feature_trend["other_args"]
        self.entry = entry

         # Input validation
        if type(self.other_args) is not dict:
            raise TypeError("Invalid other_args: other_args should be a dict")
        if self.avg_min < self.abs_min or self.avg_max > self.abs_max or self.avg_min > self.avg_max or self.abs_min > self.abs_max:
            raise ValueError("Invalid values for number ranges")
        if self.anomaly_percentage < 0 or self.anomaly_percentage > 1:
            raise ValueError("Invalid anomaly percentage: it should be between 0 and 1, inclusive")
        if not feature_trend or (type(feature_trend) is not dict):
            raise TypeError("Invalid anomaly_detection_trend: anomaly_detection_trend should be a dict, not a list")
        if entry:
            if type(entry) is str:
                try:
                    test = loads(entry)
                except:
                    raise ValueError("Invalid entry: if entry is a string, entry should only be a JSON string")
            elif type(entry) is dict or type(entry) is list:
                pass
            else:
                raise TypeError("Invalid entry: entry should only be a string, list, or dict")
        else:
            raise ValueError("Invalid entry: entry is empty")

    def generate_noise(self, initial_value):
        """
        Function that generates random noise in the data trend (used for Anomaly Detection)

        Arguments:
            - initial_value: A numeric value (int, float, etc.) to potentially throw an anomaly

        Returns:
            - A numeric value representing the new field value

        Raises:
            - TypeError: initial_value should be a numeric value
        """

        # Input validation
        if type(initial_value) is not int and type(initial_value) is not float:
            raise TypeError("initial_value should be a numeric value")

        new_value = initial_value

        # noise: this variable "flips" a weighted "coin" to determine whether to throw an anomaly
        noise = randint(1, 1000) / 1000

        # If an anomaly chance is enabled, change the value and return it
        # If noise is greater than the anomaly percentage, do not change the intial value
        if noise <= self.anomaly_percentage:
            min_or_max = randint(0,1)
            kind = None
            if type(initial_value) is int:
                kind = "integer"
                if not min_or_max:
                    new_value = choose_field(kind, [self.avg_max, self.abs_max])
                else:
                    new_value = choose_field(kind, [self.abs_min, self.avg_min])
            else:
                kind = str(type(initial_value)).split("\'")[1]
                if not min_or_max:
                    self.other_args.update({"min_value": self.avg_max, "max_value": self.abs_max})
                    new_value = choose_field(kind, [self.other_args])
                else:
                    self.other_args.update({"min_value": self.abs_min, "max_value": self.avg_min})
                    new_value = choose_field(kind, [self.other_args])
        return new_value

    def generate_data_trend(self):
        """
        Function that generates data that simulates a trend with or without anomalies

        Returns:
            - An array of generated data (if the entry was a list) or an individual entry as a JSON string
        """
        data_entry = None

        entry = self.entry
        milliseconds = int(self.current_date.strftime("%s")) * 1000

        # If entry came from an input file, load data to the dataset list
        if type(entry) is list:
            data_entry = []
            for element in entry:
                element = loads(element)
                element[self.feature] = self.generate_noise(self, element[self.feature])
                element[self.timestamp] = milliseconds
                element = dumps(element)
                data_entry.append(element)
        else:
            if type(entry) is str:
                entry = loads(entry)
            entry[self.feature] = self.generate_noise(entry[self.feature])

            # Update timestamp with current time
            entry[self.timestamp] = milliseconds
            data_entry = dumps(entry)

        return data_entry
