"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch

# Standard libraries
from datetime import date, timedelta, datetime
from os import environ, remove, listdir, path
from argparse import ArgumentParser
from time import sleep
from math import ceil
from json import load
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_authentication.sample_data_basic_authentication import BasicAuthentication
from sample_data_authentication.sample_data_authentication import Authentication
from sample_data_commons.utils import unzip_file, validate_job_args, untar_file
from sample_data_indices.sample_data_indices import SampleDataIndex
from sample_data_plugins.ad_plugin_class import AnomalyDetection


# Constants
DIR_PATH = path.dirname(path.realpath(__file__))
MINUTES_PER_DAY = 1440


# Various arguments to configure where config files are and what credentials to use for OS
parser = ArgumentParser(description= "Configure credentials for OS connection")
parser.add_argument("-host", help = "The hostname (without the scheme)", default = environ.get("HOST"))
parser.add_argument("-username", help = "The username of OS with CRUD permissions", default = environ.get("SAMPLE_DATA_USERNAME"))
parser.add_argument("-password", help = "The password of OS with CRUD permissions", default = environ.get("SAMPLE_DATA_PASSWORD"))
parser.add_argument("-port", help = "The port number in which OS will listen to", type = int, default = 9200)
parser.add_argument("-config_path", help = "The directory where plugin configurations are found", default = path.join(DIR_PATH.replace("/sample_data_jobs", ""), "config"))
args = parser.parse_args()


# Default configs for startup job
URL = "https://" + args.host
HEADER = BasicAuthentication(args.username, args.password)
CLIENT = OpenSearch(
    hosts = [{'host': args.host, 'port': args.port}],
    http_compress = True,
    http_auth = (args.username, args.password),
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)


def startup_job(config_path:str = args.config_path,
    url:str = URL,
    header:Authentication = HEADER,
    client:OpenSearch = CLIENT
):
    """
    Given various arguments, create indices, ingest data into them, and initialize/startup plugins

    Arguments:
        - config_path: The directory path in which the plugin config json files are located
        - url: The base url in which the API can be called
        - header: The Authentication object used to create and return request headers
        - client: The OpenSearch Python client object used to create and ingest indices

    Raises:
        - KeyError: One or more of the following required keys are missing: ingest_args, index_name, index_body, days_before, days_after, create_payload, plugin
        - KeyError: index_name not found; index_name is a required argument in \"ingest_args\"
        - ConnectionError: Startup index ingestion failed to start; check the config file or connection settings
        - ConnectionError: Startup anomaly detector failed; Check host, username, and password, and/or any connection settings
    """

    # First validate input
    validate_job_args(config_path, url, header, client)

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
            # Add to files to be removed
            if file != filename:
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
                        create_payload = config["create_payload"]
                        plugin = config["plugin"]
                    except:
                        raise KeyError("One or more of the following required keys are missing: ingest_args, index_name, index_body, days_before, days_after, create_payload, plugin")

                    # Generate date range of indices (or just 1 if days_after and days_before is 0)
                    for day in range(days_after + days_before + 1):
                        ingest_args["current_date"] = datetime.now()
                        ingest_args.pop("index_name")

                        try:
                            index_name_to_create = index_name
                        except:
                            raise KeyError("index_name not found; index_name is a required argument in \"ingest_args\"")

                        # If user specifies minute intervals, number variable will be updated
                        if "minutes" in ingest_args:
                            ingest_args["number"] = ceil(MINUTES_PER_DAY/ingest_args["minutes"])

                        # If user specifies a date range, index names with dates are appended
                        if days_after or days_before:
                            calculated_date = date.today() - timedelta(days = (days_before - day))
                            calculated_date = datetime(calculated_date.year, calculated_date.month, calculated_date.day)
                            index_name_to_create = index_name + "_" + str(calculated_date.month) + "_" + str(calculated_date.day) + "_" + str(calculated_date.year)
                            ingest_args["current_date"] = calculated_date

                        # Whether the index exists or not, a new index object is created
                        new_index = SampleDataIndex(index_name_to_create, index_body, client)

                        # Update the index_name in ingest_args
                        ingest_args["index_name"] = index_name_to_create

                        # If an index exists, we do not ingest more data as it is assumed that the data is already ingested
                        if not client.indices.exists(index = index_name_to_create):
                            try:
                                new_index.create_index()
                                new_index.ingest_more(**ingest_args)
                            except Exception as e:
                                print(e)
                                raise ConnectionError("Startup index ingestion failed to start; check the config file or connection settings")

                    # # Sleep is needed here for the indices to be added and ingested
                    # # If it isn't added, then the anomaly detector cannot be created
                    sleep(1)

                    # If the desired plugin was anomaly detection, the plugin is created and jobs ran
                    if plugin == "anomaly_detection":
                        new_detector = AnomalyDetection(index_name = index_name + "*", target_index = "opensearch-ad-plugin-result-index", payload = create_payload, base_url = url, days_ago = days_before, auth = header)
                        try:
                            new_detector.create_detector()
                            new_detector.start_detector()
                            new_detector.start_detector(True)
                        except Exception as e:
                            print(e)
                            raise ConnectionError("Startup anomaly detector failed; Check host, username, and password, and/or any connection settings")

    # Deletes all unzipped config files at the end
    for file in file_removal_array:
        remove(file)


# Starts job upon execution of script
if __name__ == "__main__":
    startup_job()
