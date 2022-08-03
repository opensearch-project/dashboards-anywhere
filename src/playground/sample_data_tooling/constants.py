"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from os import environ, path

PORT = 9200
MINUTES_PER_DAY = 1440
HOST = environ.get("SAMPLE_DATA_HOST")
SAMPLE_DATA_USERNAME = environ.get("SAMPLE_DATA_USERNAME")
SAMPLE_DATA_PASSWORD = environ.get("SAMPLE_DATA_PASSWORD")
DIR_PATH = path.join(path.dirname(path.realpath(__file__)), "config")
SCHEME = "https://"
