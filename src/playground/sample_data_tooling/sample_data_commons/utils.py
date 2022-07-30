"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0

utils.py contains the small utility functions needed throughout the tool

Functions:
    - validate_filename(): Function that validates the filename is a json, ndjson, or csv file
"""

def validate_filename(filename):
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
