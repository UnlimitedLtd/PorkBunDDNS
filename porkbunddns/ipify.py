"""
Interact with the IPify REST API. 
For more information see https://www.ipify.org
"""

import dataclasses
import logging

import pydantic
import requests

logger = logging.getLogger(__name__)


class IPifyResponseModel(pydantic.BaseModel):
    """ Response body from IPify. """

    ip: str


@dataclasses.dataclass
class IP:
    """ Holds IP information. """

    ip: str


class IPify:  # pylint: disable=too-few-public-methods
    """
    Interact with the IPify REST API.
    For more information see https://www.ipify.org
    """

    _IPIFY_API_ENDPOINT = "https://api.ipify.org/?format=json"

    def __init__(self, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        if verbose:
            logger.setLevel(logging.DEBUG)

    def get_current_ip(self) -> IP:
        """
        Get current IP address.

        Returns:
            IP: Current IP address object.
        """

        response = requests.get(
            url=self._IPIFY_API_ENDPOINT, timeout=self.timeout)
        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        response.raise_for_status()

        parsed = IPifyResponseModel.model_validate_json(response.content)

        return IP(ip=parsed.ip)
