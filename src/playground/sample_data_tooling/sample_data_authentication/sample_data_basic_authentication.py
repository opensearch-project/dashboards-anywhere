"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""

from base64 import b64encode
from os import path
import sys

# Adds parent directory "/sample_data_tooling" to sys.path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from sample_data_authentication.sample_data_authentication import Authentication


class BasicAuthentication(Authentication):
    """
    BasicAuthentication: derived from Authentication class

    Arguments:
        - username: the username with create, write, and delete access (typically the admin)
        - password: the password with create, write, and delete access (typically the admin)
    """
    def __init__(self, username:str, password:str):
        self.__auth = username + ":" + password

    def get_auth(self) -> dict:
        """
        Function that returns the headers with authentication for use with the plugin

        Returns:
            - A dict containing the headers needed to connect to OS
        """
        __auth_encode = b64encode(self.__auth.encode("ascii"))
        __authorization = "Basic " + str(__auth_encode).split("\'")[1]
        return {
            'Authorization': __authorization,
            'Content-Type': 'application/json'
        }