"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0

utils.py contains the small utility functions needed throughout the tool

Functions:
    - validate_filename(): Function that validates the filename is a json, ndjson, or csv file
    - unzip_file(): Function that unzips a filename if it was zipped.
    - validate_job_args(): Function that validates various arguments for the startup and refresh jobs
    - untar_file(): Function that extracts files from a tar.gz file
"""

from opensearchpy import OpenSearch

# Standard libraries
from shutil import copyfileobj
from os import path
import tarfile
import gzip
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.sample_data_authentication.sample_data_authentication import Authentication


def validate_filename(filename:str):
    """
    Validates that the filename is a string and that the file is a json, ndjson, or csv file

    Arguments:
        - filename: The object to validate

    Raises:
        - TypeError: filename should be a string
        - ValueError: filename must be a .json, .ndjson, or .csv file
    """
    if type(filename) is not str:
        raise TypeError("filename should be a string")
    if ".json" not in filename and ".csv" not in filename and ".ndjson" not in filename:
        raise ValueError("filename must be a .json, .ndjson, or .csv file")


def unzip_file(filename:str) -> str:
    """
    Given a filename, if it is zipped, unzip into a new file and return the new filename

    Arguments:
        - filename: The filename to potentially unzip

    Returns:
        - The unzipped filename (or None if the filename is invalid)
    """

    # Ignores non json or ndjson files
    if type(filename) is not str or (".json" not in filename):
        return None

    # For already unzipped files
    if type(filename) is str and ".gz" not in filename:
        print("Payload is already unzipped")
        return filename

    with gzip.open(filename, 'rt') as fin:
        with open(filename.split(".gz")[0], 'wt') as fout:
            copyfileobj(fin, fout)

    return filename.split(".gz")[0]


def validate_job_args(config_path:str = None,
    url:str = None,
    header:Authentication = None,
    client:OpenSearch = None
):
    """
    Given various arguments, validate input type

    Arguments:
        - config_path: The directory path in which the plugin config json files are located
        - url: The base url in which the API can be called
        - header: The Authentication object used to create and return request headers
        - client: The OpenSearch Python client object used to create and ingest indices

    Raises:
        - TypeError: config_path should be a string
        - TypeError: url should be a string
        - TypeError: header should be a subclass of Authentication
        - TypeError: client should be a OpenSearch Python client object
    """
    if config_path and type(config_path) is not str:
        raise TypeError("config_path should be a string")
    if url and type(url) is not str:
        raise TypeError("url should be a string")
    if header and not isinstance(header, Authentication):
        raise TypeError("header should be a subclass of Authentication")
    if client and not isinstance(client, OpenSearch):
        raise TypeError("client should be a OpenSearch Python client object")


def untar_file(filename:str, destination:str = None) -> list:
    """
    Utility function that extracts tar files and returns the filenames

    Arguments:
        - filename: The filename (as a tar.gz file) to extract
        - destination: The destination directory to store the files

    Returns:
        - A list of filenames extracted from the tar file (or none if the filename isn't a tar file)
    """

    # Ignores non-filenames or non-tar.gz files
    if type(filename) is not str or ".tar.gz" not in filename or type(destination) is not str:
        return []

    t_file = tarfile.open(filename)

    filename_list = []

    # Put files into a desired directory, if specified
    if destination:
        t_file.extractall(destination)
        for file in t_file.getnames():
            filename_list.append(path.join(destination, file))
    else:
        t_file.extractall()
        filename_list = t_file.getnames()

    return filename_list
