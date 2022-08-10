"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from opensearchpy import OpenSearch

# Standard Libraries
from os import path
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.abspath(__file__).split("sample_data_tooling")[0])
from sample_data_tooling.sample_data_ingestor.sample_data_ingestor import ingest


class SampleDataIndex:
    """
    Index class: this class can create, delete, and ingest more data into a new or existing index

    Arguments:
        - index_name: The index name to create/ingest/delete
        - index_body: The body containing the configurations of the index (used for index creation)
        - client: an OpenSearch Python client object

    Raises:
        - TypeError: Invalid index_name: index_name is a string representing the target index name
        - TypeError: Invalid index_body: index_body should be a dict defined in the config JSON file
        - TypeError: client should be an OpenSearch Python client object
    """

    def __init__(self, index_name:str, index_body:dict, client:OpenSearch):
        # Validate input
        if type(index_name) is not str:
            raise TypeError("Invalid index_name: index_name is a string representing the target index name")
        if type(index_body) is not dict:
            raise TypeError("Invalid index_body: index_body should be a dict defined in the config JSON file")
        if client and (not isinstance(client, OpenSearch)):
            raise TypeError("client should be an OpenSearch Python client object")

        self.index_name = index_name
        self.index_body = index_body
        self.client = client

    def create_index(self):
        """
        Checks if an index exists; if not, the index is created using the OpenSearch Python client
        (client is defined in the startup/refresh jobs)

        Raises:
            - ConnectionError: Index failed to be created; check the client and/or index configurations
        """

        if not self.client.indices.exists(index = self.index_name):
            try:
                self.client.indices.create(index = self.index_name, body=self.index_body)
            except Exception as e:
                print(e)
                raise ConnectionError("Index failed to be created; check the client and/or index configurations")
            print("The index %s was successfully created" % (self.index_name))
        else:
            print("The index %s exists already" % (self.index_name))

    def delete_index(self):
        """
        Checks if an index exists; if it does, the index is deleted using the OpenSearch Python client
        (client is defined in the startup/refresh jobs)

        Raises:
            - ConnectionError: Index failed to be deleted; check the index name and/or client configurations
        """
        if self.client.indices.exists(index = self.index_name):
            try:
                self.client.indices.delete(index = self.index_name)
            except Exception as e:
                print(e)
                raise ConnectionError("Index failed to be deleted; check the index name and/or client configurations")
            print("The index %s was successfully deleted" % (self.index_name))
        else:
            print("The index %s does not exist" % (self.index_name))

    def ingest_more(self, **kwargs):
        """
        Calls the ingest() function to ingest more data using provided key word arguments
        """
        try:
            ingest(client = self.client, **kwargs)
        except Exception as e:
            print(e)
            print("Check configurations again; additionally, the index should be created before it can be ingested")
            raise
