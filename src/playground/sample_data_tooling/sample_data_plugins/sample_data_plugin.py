"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from json import dumps, load, loads
from shutil import copyfileobj
from os import path, remove
import gzip
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_authentication.sample_data_authentication import Authentication
from sample_data_commons.validate_filename import validate_filename


class Plugin:
    """
    Generic Plugin class: initialization is defined here

    Arguments:
        - index_name: The name of the source index
        - payload: The JSON body of which to call create API requests
        - base_url: The IP address/url where the OpenSearch backend lies
        - auth: The Authentication object needed to get headers from

    Raises:
        - TypeError: Invalid index_name: index_name is a string representing the target index name
        - TypeError: Invalid base_url: base_url is a url string
        - TypeError: Invalid payload: payload needs to be a dict, JSON string, or filename string
        - TypeError: Invalid auth: auth needs to be an Authentication instance
        - NotImplementedError: Headers failed to be obtained because the Authentication subclass instance did not implement get_auth()
    """

    def __init__(self, index_name:str, payload, base_url:str, auth:Authentication):
        # Validate input
        if type(index_name) is not str:
            raise TypeError("Invalid index_name: index_name is a string representing the target index name")
        if type(base_url) is not str:
            raise TypeError("Invalid base_url: base_url is a url string")
        if type(payload) is not str and type(payload) is not dict:
            raise TypeError("Invalid payload: payload needs to be a dict, JSON string, or filename string")
        if not isinstance(auth, Authentication):
            raise TypeError("Invalid auth: auth needs to be an Authentication instance")
        
        self.index_name = index_name
        self.id = None
        self.payload = payload
        
        # Convert to JSON string if necessary
        if type(self.payload) is dict:
            self.payload = dumps(self.payload)
        
        # Add authentication headers
        try:
            self.headers = auth.get_auth()
        except Exception as e:
            print(e)
            raise NotImplementedError("Headers failed to be obtained because the Authentication subclass instance did not implement get_auth()")

        # Build url
        self.base_url = base_url
        if self.base_url.endswith("/"):
          self.base_url = self.base_url[:-1]
        self.url = self.base_url + ":9200/"
    
    def unzip(self) -> str:
        """
        Utility function wherein if payload is a zipped config filename, unzip it and return unzipped filename

        Returns:
            - A filename string of the unzipped file

        Raises:
            - TypeError: Payload is not a .json file
        """
        
        # Input validation
        validate_filename(self.payload)
        if ".json" not in self.payload:
            raise ValueError("Payload is not a .json file")

        # If the filename (represented as payload) was already unzipped, return payload
        if type(self.payload) is str and ".gz" not in self.payload:
            print("Payload is already unzipped")
            return self.payload
        
        # Unzip contents and and copy the zipped contents to a new unzipped file
        with gzip.open(self.payload, 'rt') as fin:
            with open(self.payload.split(".gz")[0], 'wb') as fout:
                copyfileobj(fin, fout)

        return self.payload.split(".gz")[0]

    def convert_payload(self, payload, plugin_config_directory_name:str) -> dict:
        """
        Utility function to convert payload to a dict

        Arguments:
            - payload: A payload used for request calls; can be a dict, JSON string, or filename
            - plugin_config_directory_name: The directory in "config/" where the payload (if it was a filename)
              can be accessed

        Returns:
            - A payload converted to a dict

        Raises: 
            - TypeError: Invalid plugin_config_directory_name: plugin_config_directory_name should be a string
            - TypeError: Invalid payload string: payload should be a filename string or a JSON string
            - TypeError: payload can only be a dict, a string filename, or a JSON string
            - TypeError: Invalid payload: payload can be a dict or a string only
            - TypeError: Payload should be a JSON string
        """

        # Input validation
        if type(plugin_config_directory_name) is not str:
            raise TypeError("Invalid plugin_config_directory_name: plugin_config_directory_name should be a string")
        if type(payload) is not str and type(payload) is not dict:
            raise TypeError("payload can only be a dict, a string filename, or a JSON string")
        
        # If payload is a JSON string, try to load it as a dict
        if type(payload) is str and ".json" not in payload:
            try:
                    payload = loads(payload)
            except Exception as e:
                print(e)
                raise TypeError("Payload should be a JSON string")

        try:
            # If payload is a config file, navigate to the config file and load contents to payload (unzip if necessary)
            if type(self.payload) is str and ".json" in self.payload:
                dir_path = path.dirname(path.realpath(__file__))
                dir_path = dir_path.split("/sample_data_plugin")[0]
                config_file = self.unzip()
                dir_path += "/config/" + plugin_config_directory_name + "/" + config_file
                with open (dir_path, "r") as f:
                    payload = load(f)

                # If the file was previously unzipped, remove the unzipped file
                if config_file != self.payload:
                    remove(config_file)
        except:
            # Try opening the filename directly if the directory cannot be found
            try:
                config_file = self.unzip()
                with open(config_file, "r") as f:
                    payload = load(f)
                if config_file != self.payload:
                    remove(config_file)
            except Exception as e:
                print(e)
                raise TypeError("Invalid payload string: payload should be a filename string or a JSON string")
        
        # Input validation to ensure payload can only be a dict (in case payload wasn't a string or dict before)
        if type(payload) is not dict:
            raise TypeError("Invalid payload: payload can be a dict or a string only")

        return payload