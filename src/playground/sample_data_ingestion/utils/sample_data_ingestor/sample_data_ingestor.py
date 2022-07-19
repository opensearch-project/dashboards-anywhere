from datetime import datetime, timedelta
from shutil import copyfileobj
from json import loads, dumps
from os import remove, path
from random import randint
import gzip
import sys
import csv

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_generator.sample_data_generator import generate_data
from sample_data_generator.sample_data_generator import choose_field


"""
Function that generates random noise in the data trend (used for Anomaly Detection)
Arguments:
    - initial_value: The original non-anomaly value generated from generate_data_trend()
    - anomaly_percentage: How often an anomaly occurs (minimum: 0.001)
    - avg_min: The lowest average value in which there is no anomaly
    - avg_max: The highest average value in which there is no anomaly
    - abs_min: The lowest possible value, which can be an anomaly
    - abs_max: The highest possible value, which can be an anomaly
"""
def generate_noise(initial_value, anomaly_percentage, avg_min, avg_max, abs_min, abs_max):
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


"""
Function that generates data that simulates a trend with or without anomalies
Arguments:
    - input: The template (JSON, mapping, CSV)
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
"""
def generate_data_trend(
    input, 
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
    dataset = []

    for i in range(number):
        entry = generate_data(input, mapping) 
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


"""
Function that ingests user-provided data or generated data
Arguments:  
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
"""
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
    current_date = datetime.today()
):
    # Various errors for invalid arguments
    if not template or not index_name:
        raise ValueError("You must have a template and an index name to continue")
    if not client:
        raise ValueError("Client needed to connect")
    if avg_min < abs_min or avg_max > abs_max or avg_min > avg_max or abs_min > abs_max:
        raise ValueError("Check ranges for generating trend data")
    if anomaly_percentage < 0 or anomaly_percentage > 1:
        raise ValueError("Anomaly percentage cannot be outside a percent")

    dataset = []
    initial_time = None

    # If the user provides their own data
    if file_provided:
        name = template
        # Unzips file 
        if ".gz" in name:
            with gzip.open(input, 'rt') as fin:
                    with open(input.split(".gz")[0], 'wb') as fout:
                        copyfileobj(fin, fout)
                    name = input.split(".gz")[0]
        # Reads from CSV
        if ".csv" in name:
            with open(name, "r") as f:
                reader = csv.reader(f)
                fields = next(reader)
                for row in reader:
                    entry = {}
                    for i in range(len(fields)):
                        entry[fields[i]] = row[i]
                    if not initial_time and timestamp:
                        initial_time = entry[timestamp]
                    dataset.append(entry)
        # Reads from JSON 
        elif ".json" in name:
            with open(name, "r") as f:
                for line in f:
                    if not initial_time and timestamp:
                        temp = loads(line)
                        initial_time = temp[timestamp]
                    dataset.append(loads(line))
        
        # Removes zipped file
        if template != name:
            remove(name)

    # If anomalies wanted to be generated
    elif anomaly_percentage:
        dataset = generate_data_trend(input = template, 
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
    one_week_ago = datetime.now() - timedelta(days = 7)
    while i < len(dataset):
        j = i
        tosend = []
        while j < min(i + chunk, len(dataset)):
            tosend.append({"index": {"_index": index_name}})

            # If timestamps were a field type for user provided data, modify time
            if file_provided and timestamp:
                one_week_ago += timedelta(minutes = minutes)
                offset = one_week_ago.strftime("%s")
                dataset[j][timestamp] = int(offset)
            tosend.append(dataset[j])
            j+= 1
        
        response = client.bulk(
            body = tosend
        )
        print("\nAdding documents:")
        print(response)
        i += chunk
    return dataset