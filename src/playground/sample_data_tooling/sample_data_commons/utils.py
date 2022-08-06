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
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_authentication.sample_data_authentication import Authentication


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