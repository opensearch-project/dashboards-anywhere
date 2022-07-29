"""
Copyright OpenSearch Contributors
SPDX-License-Identifier: Apache-2.0
"""


class Authentication:
    """
    Abstract class for returning headers. Nothing is defined here but there should be only one method: get_auth()

    Raises:
        - NotImplementedError: get_auth() should be implemented for every Authentication subclass
    """

    def __init__(self):
        pass

    def get_auth(self):
        """
        This method should return the headers necessary to connect to OS clusters

        Returns:
            - Requires a dict to be returned
        """
        raise NotImplementedError("get_auth() should be implemented for every Authentication subclass")
