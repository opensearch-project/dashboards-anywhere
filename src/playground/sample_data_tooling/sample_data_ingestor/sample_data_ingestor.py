"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch

# Standard libraries
from datetime import datetime, timedelta
from shutil import copyfileobj
from json import loads, dumps
from os import remove, path
import gzip
import sys
import csv

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_generator.sample_data_generator import generate_data
from sample_data_plugins.ad_plugin_data_config.average_trend_class import AverageTrend
from sample_data_commons.utils import validate_filename


def ingest_from_user_data(filename:str) -> list:
    """
    Utility function that loads user provided data to a list

    Arguments:
        - filename: The name of the user provided data file as a .json or .csv file (zipped or unzipped)

    Returns:
        - A list of data loaded from the file

    Raises:
        - ValueError: .json, .ndjson, and .csv files are only supported
    """

    # Input validation
    validate_filename(filename)
    name = filename.split(".gz")[0]
    dataset = []

    # Unzips file
    if ".gz" in name:
        with gzip.open(name, 'rt') as fin:
                with open(name.split(".gz")[0], 'wb') as fout:
                    copyfileobj(fin, fout)
    # Reads from CSV
    if ".csv" in name:
        with open(name, "r") as f:
            reader = csv.reader(f)
            fields = next(reader)
            for row in reader:
                entry = {}
                for i in range(len(fields)):
                    entry[fields[i]] = row[i]
                dataset.append(entry)
    # Reads from JSON
    elif ".json" in name or ".ndjson" in name:
        with open(name, "r") as f:
            for line in f:
                dataset.append(loads(line))
    else:
        raise ValueError(".json, .ndjson, and .csv files are only supported")

    # Removes unzipped file
    if filename != name:
        remove(name)

    return dataset


def ingest_validation(client:OpenSearch = None,
    data_template = None,
    index_name:str = None,
    file_provided:bool = None,
    mapping:bool = None,
    number:int = None,
    chunk:int = None,
    timestamp:str = None,
    minutes:int = None,
    current_date:datetime = None,
    max_bulk_size:int = None,
    anomaly_detection_trend:list = None
):
    """
    Function that raises errors for improper arguments

    Arguments (all optional):
        - client: an OpenSearch Python client object
        - data_template: JSON file, CSV file, JSON mapping, or JSON short-hand template
        - index_name: The name of the index to ingest data
        - mapping: Whether or not the input is a mapping
        - file_provided: Boolean flag as to whether or not a file was provided
        - chunk: How many documents can be ingested per BULK call
        - timestamp: The field name that contains timestamps
        - number: How many documents to generate
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another)
        - current_date: The date at which entries are generated
        - max_bulk_size: The max amount in bytes of a bulk call

    Raises:
        - TypeError: client should be an OpenSearch Python client object
        - TypeError: data_template should be a filename string, a JSON string, or dict
        - TypeError: index_name should be a string
        - TypeError: file_provided should be a boolean flag
        - TypeError: mapping should be a boolean flag, not a data template
        - ValueError: number should be a positive integer
        - ValueError: chunk should be a positive integer
        - TypeError: timestamp should be the field name that contains the timestamp, not the actual unix timestamp
        - ValueError: minutes should be a positive integer
        - ValueError: current_date should be a datetime object
        - ValueError: max_bulk_size should be a positive integer
        - TypeError: anomaly_detection_trend should be a list of config dicts
    """
    if client and (not isinstance(client, OpenSearch)):
        raise TypeError("client should be an OpenSearch Python client object")
    if data_template and type(data_template) is not str and type(data_template) is not dict:
        raise TypeError("data_template should be a filename string, a JSON string, or dict")
    if index_name and type(index_name) is not str:
        raise TypeError("index_name should be a string")
    if file_provided and type(file_provided) is not bool:
        raise TypeError("file_provided should be a boolean flag")
    if mapping and type(mapping) is not bool:
        raise TypeError("mapping should be a boolean flag, not a data template")
    if number and type(number) is not int or (type(number) is int and number < 0):
        raise ValueError("number should be a positive integer")
    if chunk and type(chunk) is not int or (type(chunk) is int and chunk < 0):
        raise ValueError("chunk should be a positive integer")
    if timestamp and type(timestamp) is not str:
        raise TypeError("timestamp should be the field name that contains the timestamp, not the actual unix timestamp")
    if minutes and type(minutes) is not int or (type(minutes) is int and minutes < 0):
        raise ValueError("minutes should be a positive integer")
    if current_date and type(current_date) is not datetime:
        raise ValueError("current_date should be a datetime object")
    if max_bulk_size and type(max_bulk_size) is not int or (type(max_bulk_size) is int and max_bulk_size < 0):
        raise ValueError("max_bulk_size should be a positive integer")
    if anomaly_detection_trend and type(anomaly_detection_trend) is not list:
        raise TypeError("anomaly_detection_trend should be a list of config dicts")


def build_request_body(index_name:str,
    file_provided:bool,
    timestamp:str,
    minutes:int,
    chunk:int,
    current_index:int,
    dataset:list,
    max_bulk_size:int
) -> tuple:
    """
    Function that constructs the request body for BULK API call

    Arguments:
        - index_name: The name of the index to ingest data
        - file_provided: Boolean flag as to whether or not a file was provided
        - chunk: How many documents can be ingested per BULK call
        - timestamp: The field name that contains timestamps
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another)
        - current_date: The date at which entries are generated
        - dataset: The list containing the data to ingest
        - max_bulk_size: The max amount in bytes of a bulk call
        - current_index: The index representing the current document in dataset to look at

    Returns:
        - A tuple containing the request body and the current index to look at

    Raises:
        - ValueError: current_index should be a positive index position
        - TypeError: dataset is a list of documents to ingest
    """

    # First validates input
    ingest_validation(index_name = index_name,
        file_provided = file_provided,
        timestamp = timestamp,
        minutes = minutes,
        chunk = chunk,
        max_bulk_size = max_bulk_size
    )
    # Validates function specific input
    if type(current_index) is not int or (type(current_index) is int and current_index < 0):
        raise ValueError("current_index should be a positive index position")
    if type(dataset) is not list:
        raise TypeError("dataset should be a list of documents to ingest, not a dict")

    start_index = current_index
    one_week_ago = datetime.now() - timedelta(days = 7)
    add_to_request = []
    request_body = []
    current_body_size = sys.getsizeof(request_body)
    while current_index < min(start_index + chunk, len(dataset)):
        # Adds the index name
        index_name_body = {"index": {"_index": index_name}}

        # If timestamps were a field type for user provided data, modify time
        if file_provided and timestamp:
            one_week_ago += timedelta(minutes = minutes)
            offset = one_week_ago.strftime("%s")
            dataset[current_index][timestamp] = int(offset)

        # Adds the action to take
        index_action = dataset[current_index]

        # Adds both index name body and index action body to the test request body
        add_to_request.append(index_name_body)
        add_to_request.append(index_action)
        current_body_size = sys.getsizeof(add_to_request)

        # Adds to request only if the body size is < the max bulk size (user defined)
        if current_body_size < max_bulk_size:
            request_body.append(index_name_body)
            request_body.append(index_action)
        else:
            break
        current_index+= 1

    return (request_body, current_index)


def ingest(client:OpenSearch,
    data_template,
    index_name:str,
    file_provided:bool = False,
    mapping:bool = True,
    number:int = 6,
    chunk:int = 5,
    timestamp:str = None,
    minutes:int = 2,
    current_date:datetime = datetime.now(),
    max_bulk_size:int = 100000,
    anomaly_detection_trend:dict = None
) -> list:
    """
    Function that ingests user-provided data or generated data

    Arguments:
        - client: an OpenSearch Python client object
        - data_template: JSON file, CSV file, JSON mapping, or JSON short-hand template
        - index_name: The name of the index to ingest data
        - file_provided: Boolean flag as to whether or not a file was provided (default is False)
        - mapping: Whether or not the input is a mapping (default is True)
        - chunk: How many documents can be ingested per BULK call (default is 5)
        - timestamp: The field name that contains timestamps (default is None)
        - number: How many documents to generate (default is 6)
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another) (default is 2)
        - current_date: The date at which entries are generated (default is today's datetime)
        - max_bulk_size: The max amount in bytes of a bulk call (default is 100000)
        - anomaly_detection_trend: list of configurations dicts to use for generating data trends (default is None)

    Returns:
        - A list of the data that was ingested

    Raises:
        - TypeError: Request body is not a list
        - ValueError: Request body does not come in index, action pairs; an index name does not have an action or vice versa
        - ConnectionError: Index failed to be ingested. Check the client configurations
    """

    # Validates that inputs are correct
    ingest_validation(client = client,
        data_template = data_template,
        index_name = index_name,
        file_provided = file_provided,
        mapping = mapping,
        number = number,
        chunk = chunk,
        timestamp = timestamp,
        minutes = minutes,
        current_date = current_date,
        max_bulk_size = max_bulk_size,
        anomaly_detection_trend = anomaly_detection_trend
    )

    dataset = []

    # If the user provides their own data
    if file_provided:
        dataset = ingest_from_user_data(filename = data_template)

    # If anomalies wanted to be generated
    elif anomaly_detection_trend:
        for current_document_index in range(number):
            # Generate random data
            entry = generate_data(data_template, mapping)

            # For each feature needing a trend, modify that specific field value to fit a trend
            for desired_trend in anomaly_detection_trend:
                if desired_trend["data_trend"] == "AverageTrend":
                    changed_entry = AverageTrend(
                        timestamp = timestamp,
                        entry = entry,
                        feature_trend = desired_trend,
                        current_date = current_date
                    )
                    entry = changed_entry.generate_data_trend()
            dataset.append(entry)
            # Increment current date
            current_date += timedelta(minutes = minutes)
    else:
         # Generates the specified number of documents
        for current_document_index in range(number):
            entry = generate_data(data_template, mapping)
            if type(entry) is list:
                for element in entry:
                    if type(element) is str:
                        element = loads(element)
                    if timestamp:
                        element[timestamp] = current_date
                    element = dumps(element)
                    dataset.append(element)
            else:
                entry = generate_data(data_template, mapping)
                if type(entry) is str:
                    entry = loads(entry)
                if timestamp:
                    entry[timestamp] = current_date
                entry = dumps(entry)
                dataset.append(entry)
            current_date += timedelta(minutes = minutes)

    # Calls BULK API to ingest documents of size "chunk"
    current_document_index = 0
    while current_document_index < len(dataset):

        # Build request body
        request_building = build_request_body(index_name, file_provided, timestamp, minutes, chunk, current_index = current_document_index, dataset = dataset, max_bulk_size = max_bulk_size)
        request_body = request_building[0]
        current_document_index = request_building[1]

        # Validates that request_body is both a list and that it is of even length
        if type(request_body) is not list:
            raise TypeError("Request body is not a list")
        if len(request_body) % 2 != 0:
            raise ValueError("Request body does not come in index, action pairs; an index name does not have an action or vice versa")

        try:
            response = client.bulk(body = request_body)
            print("\nAdding documents:")
            print(response)
        except Exception as e:
            print(e)
            raise ConnectionError("Index failed to be ingested. Check the client configurations")

    return dataset
