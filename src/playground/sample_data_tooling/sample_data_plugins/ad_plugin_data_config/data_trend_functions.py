from datetime import datetime, timedelta
from random import randint
from json import loads, dumps
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sample_data_generator.sample_data_generator import choose_field


class DataTrend():
    """
    Generic Class that generates data based on a generic trend

    Arguments;
        - feature: The field that will be used to test anomalies
        - timestamp: The field name that contains timestamps
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another)
        - current_date: The date at which entries are generated

    Raises: 
        - TypeError: Variable \"feature\" must be a string
        - TypeError: timestamp is the field name that contains the timestamp, not the actual unix timestamp
        - ValueError: minutes must be an integer >= 0
        - TypeError: current_date is a datetime object
    """
    def __init__(self, 
        feature, 
        timestamp, 
        minutes, 
        current_date
    ):
        if type(feature) is not str:
            raise TypeError("Variable \"feature\" must be a string")
        if type(timestamp) is not str:
            raise TypeError("timestamp is the field name that contains the timestamp, not the actual unix timestamp")
        if type(minutes) is not int or (type(minutes) is int and minutes < 0):
            raise ValueError("minutes must be an integer >= 0")
        if type(current_date) is not datetime:
            raise TypeError("current_date is a datetime object")
        self.feature = feature
        self.timestamp = timestamp
        self.minutes = minutes
        self.current_date = current_date


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
        - entry: The document to have one of its field values potentially change
    
    Raises:
        - ValueError: Invalid values for number ranges
        - ValueError: Invalid anomaly percentage: it should be between 0 and 1, inclusive
        - TypeError: Invalid anomaly_detection_trend: anomaly_detection_trend should be a list, not a dict
    """
    def __init__(self,
        feature, 
        timestamp, 
        feature_trend,
        entry, 
        minutes = 2,
        current_date = (datetime.today() - timedelta(days = 7))
    ):
        super().__init__( 
            feature, 
            timestamp,
            minutes, 
            current_date
        )
        # Unpacking values from anomaly_detection_trend
        self.avg_min = feature_trend["avg_min"]
        self.avg_max = feature_trend["avg_max"]
        self.abs_min = feature_trend["abs_min"]
        self.abs_max = feature_trend["abs_max"]
        self.anomaly_percentage = feature_trend["anomaly_percentage"]
        self.entry = entry

         # Input validation
        if self.avg_min < self.abs_min or self.avg_max > self.abs_max or self.avg_min > self.avg_max or self.abs_min > self.abs_max:
            raise ValueError("Invalid values for number ranges")
        if self.anomaly_percentage < 0 or self.anomaly_percentage > 1:
            raise ValueError("Invalid anomaly percentage: it should be between 0 and 1, inclusive")
        if not feature_trend or (type(feature_trend) is not dict):
            raise TypeError("Invalid anomaly_detection_trend: anomaly_detection_trend should be a dict, not a list")
    
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
            else:
                kind = type(initial_value)
            if not min_or_max:
                new_value = choose_field(kind, [self.avg_max, self.abs_max])
            else:
                new_value = choose_field(kind, [self.abs_min, self.avg_min])
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
            entry = loads(entry)
            entry[self.feature] = self.generate_noise(entry[self.feature])
        
            # Update timestamp with current time
            entry[self.timestamp] = milliseconds
            data_entry = dumps(entry)

        return data_entry