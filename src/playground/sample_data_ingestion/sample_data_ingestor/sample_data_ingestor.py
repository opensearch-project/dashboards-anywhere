from datetime import datetime, timedelta
from shutil import copyfileobj
from json import loads, dumps
from os import remove, path
from random import randint
import gzip
import sys
import csv

# Adds parent directory "/sample_data_ingestion" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_generator.sample_data_generator import generate_data
from sample_data_generator.sample_data_generator import choose_field


def generate_noise(initial_value, anomaly_percentage, avg_min, avg_max, abs_min, abs_max):
    """
    Function that generates random noise in the data trend (used for Anomaly Detection)

    Arguments:
        - initial_value: The original non-anomaly value generated from generate_data_trend()
        - anomaly_percentage: How often an anomaly occurs (minimum: 0.001)
        - avg_min: The lowest average value in which there is no anomaly
        - avg_max: The highest average value in which there is no anomaly
        - abs_min: The lowest possible value, which can be an anomaly
        - abs_max: The highest possible value, which can be an anomaly
    
    Returns:
        - A numeric value representing the new field value
    """
    new_value = initial_value
    noise = randint(1, 1000) / 1000

    # If an anomaly chance is enabled, change the value and return it
    if noise <= anomaly_percentage:
        min_or_max = randint(0,1)
        kind = None
        if type(initial_value) is int:
            kind = "integer"
        else:
            kind = type(initial_value)
        if not min_or_max:
            new_value = choose_field(kind, [avg_max, abs_max])
        else:
            new_value = choose_field(kind, [abs_min, avg_min])
    return new_value


def generate_data_trend(
    data_template, 
    feature, 
    timestamp, 
    number, 
    avg_min, 
    avg_max, 
    abs_min, 
    abs_max, 
    anomaly_percentage = .001, 
    mapping = True, 
    minutes = 2,
    current_date = datetime.today() - timedelta(days = 7)
):
    """
    Function that generates data that simulates a trend with or without anomalies

    Arguments:
        - data_template: The template (JSON, mapping, CSV)
        - feature: The field that will be used to test anomalies
        - timestamp: The field name that contains timestamps
        - number: How many documents to generate
        - avg_min: The lowest average value in which there is no anomaly
        - avg_max: The highest average value in which there is no anomaly
        - abs_min: The lowest possible value, which can be an anomaly
        - abs_max: The highest possible value, which can be an anomaly
        - anomaly_percentage: How often an anomaly occurs (minimum: 0.001)
        - mapping: Whether or not the input is a mapping
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another)
        - current_date: The date at which entries are generated

    Returns:
        - An array of generated data, which simulates a data with a trend with some anomalies
    """
    dataset = []

    for i in range(number):
        entry = generate_data(data_template, mapping) 
        milliseconds = int(current_date.strftime("%s")) * 1000
        # If entry came from an input file, load data to the dataset list
        if type(entry) is list:
            for element in entry:
                element = loads(element)
                element[feature] = generate_noise(element[feature], anomaly_percentage, avg_min, avg_max, abs_min, abs_max)
                element[timestamp] = milliseconds
                dataset.append(element)
        else:
            entry = loads(entry)
            entry[feature] = generate_noise(entry[feature], anomaly_percentage, avg_min, avg_max, abs_min, abs_max)
        
            # Update timestamp with current time
            entry[timestamp] = milliseconds
            dataset.append(dumps(entry))
        # Increment current date
        current_date += timedelta(minutes = minutes)
    return dataset


def ingest_from_user_data(filename):
    """
    Utility function that loads user provided data to a list

    Arguments:
        - filename: The name of the user provided data file as a .json or .csv file (zipped or unzipped)

    Returns:
        - A list of data loaded from the file

    Raises:
        TypeError: Filename is not a string or is not a valid filename
    """

    # Input validation
    if type(filename) is not str or (type(filename) is str and "." not in filename):
        raise TypeError("Filename is not a string or is not a valid filename")
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
    elif ".json" in name:
        with open(name, "r") as f:
            for line in f:
                dataset.append(loads(line))
    
    # Removes zipped file
    if filename != name:
        remove(name)

    return dataset


def ingest_validation(template, index_name, client, avg_min, avg_max, abs_min, abs_max, anomaly_percentage):
    """
    Function that raises errors for improper arguments

    Arguments:
        - client: an OpenSearch Python client object
        - template: JSON file, CSV file, JSON mapping, or JSON short-hand template
        - index_name: The name of the index to ingest data
        - avg_min: The lowest average value in which there is no anomaly
        - avg_max: The highest average value in which there is no anomaly
        - abs_min: The lowest possible value, which can be an anomaly
        - abs_max: The highest possible value, which can be an anomaly
        - anomaly_percentage: How often an anomaly occurs (minimum: 0.001)

    Raises:
        - ValueError: You must have a template and an index name to continue
        - ValueError: Client needed to connect
        - ValueError: Check ranges for generating trend data
        - ValueError: Anomaly percentage cannot be outside a percent
    """
    if not template or not index_name:
        raise ValueError("You must have a template and an index name to continue")
    if not client:
        raise ValueError("Client needed to connect")
    if avg_min < abs_min or avg_max > abs_max or avg_min > avg_max or abs_min > abs_max:
        raise ValueError("Check ranges for generating trend data")
    if anomaly_percentage < 0 or anomaly_percentage > 1:
        raise ValueError("Anomaly percentage cannot be outside a percent")


def build_request_body(index_name, file_provided, timestamp, minutes, chunk, chunk_index, current_index, dataset, max_bulk_size):
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

    Returns:
        - A tuple containing the request body and the current index to look at
    """

    one_week_ago = datetime.now() - timedelta(days = 7)
    add_to_request = []
    request_body = []
    current_body_size = sys.getsizeof(request_body)
    while current_index < min(chunk_index + chunk, len(dataset)):
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


def ingest(client, 
    template,
    index_name,
    file_provided = False,  
    mapping = True,  
    number = 6, 
    chunk = 5, 
    timestamp = None,
    feature = None,  
    avg_min = 0, 
    avg_max = 0, 
    abs_min = 0, 
    abs_max = 0, 
    anomaly_percentage = 0, 
    minutes = 2,
    current_date = datetime.today(),
    max_bulk_size = 100000
):
    """
    Function that ingests user-provided data or generated data

    Arguments:  
        - client: an OpenSearch Python client object
        - template: JSON file, CSV file, JSON mapping, or JSON short-hand template
        - index_name: The name of the index to ingest data
        - mapping: Whether or not the input is a mapping
        - file_provided: Boolean flag as to whether or not a file was provided
        - chunk: How many documents can be ingested per BULK call
        - feature: The field that will be used to test anomalies
        - timestamp: The field name that contains timestamps
        - number: How many documents to generate
        - avg_min: The lowest average value in which there is no anomaly
        - avg_max: The highest average value in which there is no anomaly
        - abs_min: The lowest possible value, which can be an anomaly
        - abs_max: The highest possible value, which can be an anomaly
        - anomaly_percentage: How often an anomaly occurs (minimum: 0.001)
        - minutes: The time interval for each data point (e.g. if minutes = 2, this tool will generate entries with timestamps that are 2 minutes apart from one another)
        - current_date: The date at which entries are generated
        - max_bulk_size: The max amount in bytes of a bulk call

    Returns:
        - A list of the data that was ingested

    Raises: 
        - TypeError: Request body is not a list
        - ValueError: Request body does not come in index, action pairs; an index name does not have an action or vice versa
    """

    # Validates that inputs are correct
    ingest_validation(template, index_name, client, avg_min, avg_max, abs_min, abs_max, anomaly_percentage)

    dataset = []

    # If the user provides their own data
    if file_provided:
        dataset = ingest_from_user_data(filename = template)

    # If anomalies wanted to be generated
    elif anomaly_percentage:
        dataset = generate_data_trend(data_template = template, 
            feature = feature, 
            timestamp = timestamp, 
            number = number, 
            avg_min = avg_min, 
            avg_max = avg_max, 
            abs_min = abs_min, 
            abs_max = abs_max, 
            anomaly_percentage = anomaly_percentage, 
            mapping = mapping, 
            minutes = minutes,
            current_date = current_date
        )
    else:
         # Generates the specified number of documents
        for i in range(number):
            entry = generate_data(template, mapping)
            if type(entry) is list:
                for element in entry:
                    if timestamp:
                        element[timestamp] = current_date
                    dataset.append(element)
            else:
                entry = generate_data(template, mapping)
                if timestamp:
                    entry[timestamp] = current_date
                dataset.append(entry)
            current_date += timedelta(minutes = minutes)


    # Calls BULK API to ingest documents of size "chunk"
    i = 0
    while i < len(dataset):
        j = i

        # Build request body
        request_building = build_request_body(index_name, file_provided, timestamp, minutes, chunk, chunk_index = i, current_index = j, dataset = dataset, max_bulk_size = max_bulk_size)
        request_body = request_building[0]
        j = request_building[1]

        # Validates that request_body is both a list and that it is of even length
        if type(request_body) is not list:
            raise TypeError("Request body is not a list")
        if len(request_body) % 2 != 0:
            raise ValueError("Request body does not come in index, action pairs; an index name does not have an action or vice versa") 
            
        response = client.bulk(body = request_body)
        print("\nAdding documents:")
        print(response)
        i += (j - i)
    return dataset