"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch

# Standard libraries
from datetime import timedelta, datetime
from os import listdir, path, remove
from argparse import ArgumentParser
from math import ceil
from json import load
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.constants import MINUTES_PER_DAY, HOST, SAMPLE_DATA_PASSWORD, SAMPLE_DATA_USERNAME, PORT, DIR_PATH
from sample_data_tooling.sample_data_commons.utils import unzip_file, validate_job_args, untar_file
from sample_data_tooling.sample_data_indices.sample_data_indices import SampleDataIndex


# Various arguments to configure where config files are and what credentials to use for OS
parser = ArgumentParser(description= "Configure credentials for OS connection")
parser.add_argument("-host", help = "The hostname (without the scheme)", default = HOST)
parser.add_argument("-username", help = "The username of OS with CRUD permissions", default = SAMPLE_DATA_USERNAME)
parser.add_argument("-password", help = "The password of OS with CRUD permissions", default = SAMPLE_DATA_PASSWORD)
parser.add_argument("-port", help = "The port number in which OS will listen to", type = int, default = PORT)
parser.add_argument("-config_path", help = "The directory where plugin configurations are found", default = DIR_PATH)
args = parser.parse_args()


# Establish connection with OS
CLIENT = OpenSearch(
    hosts = [{'host': args.host, 'port': args.port}],
    http_compress = True,
    http_auth = (args.username, args.password),
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)


def refresh_job(config_path:str = args.config_path, client:OpenSearch = CLIENT):
    """
    Given various arguments, delete old indices, and create and ingest new indices

    Arguments:
        - config_path: The directory path in which the plugin config json files are located
        - client: The OpenSearch Python client object used to create and ingest indices

    Raises:
        - KeyError: One or more of the following required keys are missing: ingest_args, index_name, index_body, days_before, days_after
        - ConnectionError: Refresh job failed to delete indices: check client configurations or config file configurations
        - ConnectionError: Refresh job failed to ingest indices: check client configurations or config file configurations
    """

    # First validate input
    validate_job_args(config_path = config_path, client = client)

    # Array in which unzipped files will be removed
    file_removal_array = []

    # Checking for tar files before iterating again
    for file in listdir(config_path):
        # Extracts any tar files (and adds the filenames to a filename removal array)
        file_removal_array.extend(untar_file(path.join(config_path, file), config_path))

    # Opening each config file for each plugin
    for file in listdir(config_path):
        # Unzip file and get filename
        filename = unzip_file(file)

        # If the file is a JSON file
        if filename:
            # Remove copied unzipped file, if necessary
            if filename != file:
                file_removal_array.append(filename)

            # Open the file
            with open(path.join(config_path, filename), 'r') as f:
                config = load(f)

                # If the config file is indeed a config file and not a datafile, continue
                if "plugin" in config:
                    # Arguments
                    try:
                        ingest_args = config["ingest_args"]
                        index_name = ingest_args["index_name"]
                        index_body = config["index_body"]
                        days_before = int(config["days_before"])
                        days_after = int(config["days_after"])
                    except:
                        raise KeyError("One or more of the following required keys are missing: ingest_args, index_name, index_body, days_before, days_after")

                    response = client.indices.get(index = (index_name + "*"))

                    # If user specifies a date range, index names with dates are appended
                    if days_after or days_before:
                        for key in response:
                            year = int(key.split("_")[3])
                            day = int(key.split("_")[2])
                            month = int(key.split("_")[1])

                            # Deletes indices > the amount of days before
                            if (datetime.today() - datetime(year, month, day)).days > days_before:
                                index_to_delete = index_name + "_" + str(month) + "_" + str(day) + "_" + str(year)
                                try:
                                    client.indices.delete(index = index_to_delete)
                                except Exception as e:
                                    print(e)
                                    raise ConnectionError("Refresh job failed to delete indices: check client configurations or config file configurations")
                                print("Deleted index %s" % (index_to_delete))

                        # If user specifies minute intervals, number variable will be updated
                        if "minutes" in ingest_args:
                            ingest_args["number"] = ceil(MINUTES_PER_DAY/ingest_args["minutes"])

                        # Creates and ingests data for each day after today until days_after variable
                        for day in range(days_after + 1):
                            # Creates a new index class with the new date
                            new_index_date = datetime.now() + timedelta(days = day)
                            new_index_name = index_name + "_" + str(new_index_date.month) + "_" + str(new_index_date.day) + "_" + str(new_index_date.year)
                            new_index_date = datetime(new_index_date.year, new_index_date.month, new_index_date.day)
                            new_index = SampleDataIndex(new_index_name, index_body, client)

                            # Adds modified fields to argument dict
                            ingest_args["index_name"] = new_index_name
                            ingest_args["current_date"] = new_index_date

                            # If the index doesn't already exist, create it and ingest data into it
                            if not client.indices.exists(index = new_index_name):
                                try:
                                    new_index.create_index()
                                    new_index.ingest_more(**ingest_args)
                                except Exception as e:
                                    print(e)
                                    raise ConnectionError("Refresh job failed to ingest indices: check client configurations or config file configurations")

    # Deletes all unzipped config files at the end
    for file in file_removal_array:
        remove(file)


# Starts job upon execution of script
if __name__ == "__main__":
    refresh_job()
