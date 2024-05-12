"""
Interact with the PorkBun REST API. 
For more information see https://porkbun.com/api/json/v3/documentation
"""

import dataclasses
import logging
import typing

import pydantic
import requests

logger = logging.getLogger(__name__)


class DNSARecordModel(pydantic.BaseModel):
    """ Models a DNS A record item. """

    name: str
    type: typing.Literal["A"]
    content: str
    ttl: str


class DNSARecordResponseModel(pydantic.BaseModel):
    """ Reponse body from PorkBun DNS A record lookup. """

    status: typing.Literal["SUCCESS"]
    records: typing.List[DNSARecordModel]

    @classmethod
    @pydantic.validator("records")
    def check_records_length(cls, v):
        """ Validate records is a list of length 1. """

        if len(v) != 1:
            raise ValueError("Records list must contain exactly one item")
        return v

    @property
    def record(self) -> dict:
        """ Convenience property to get first item in list. """

        return self.records[0]


@dataclasses.dataclass
class ARecord:
    """ Holds data for a domain's DNS A record. """

    ip: str
    ttl: int


class PorkBun:
    """ 
    Interact with the PorkBun REST API. 
    For more information see https://porkbun.com/api/json/v3/documentation 
    """

    _PORKBUN_API_GET_ENDPOINT = "https://porkbun.com/api/json/v3/dns/retrieveByNameType/{domain}/A/"
    _PORKBUN_API_EDIT_ENDPOINT = "https://porkbun.com/api/json/v3/dns/editByNameType/{domain}/A/"

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        self.api_key = api_key
        self.api_secret = api_secret
        if verbose:
            logger.setLevel(logging.DEBUG)

    def get_a_record(self, domain: str) -> ARecord:
        """
        Get a domain's DNS A record.

        Args:
            domain: Domain to get A record for.

        Returns:
            ARecord: Domain A record object.

        Raises:
            HTTPError: If the is a HTTP error.
        """

        response = requests.post(
            url=self._PORKBUN_API_GET_ENDPOINT.format(domain=domain),
            timeout=self.timeout,
            json={
                "secretapikey": self.api_secret,
                "apikey": self.api_key
            }
        )

        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        response.raise_for_status()

        parsed = DNSARecordResponseModel.model_validate_json(response.content)

        return ARecord(ip=parsed.record.content, ttl=int(parsed.record.ttl))

    def update_a_record(self, domain: str, ip: str, ttl: int = 600) -> None:
        """
        Update a domain DNS A record.

        Args:
            domain: Domain to update DNS A record for.
            ip: IP address to set to.
            ttl: DNS TTL, defaults to 600.

        Raises:
            HTTPError: If the is a HTTP error.
        """

        response = requests.post(
            url=self._PORKBUN_API_EDIT_ENDPOINT.format(domain=domain),
            timeout=self.timeout,
            json={
                "secretapikey": self.api_secret,
                "apikey": self.api_key,
                "content": ip,
                "ttl": str(ttl)
            },
        )

        logger.debug(
            "Request URL: %s, Status Code: %d",
            response.request.url,
            response.status_code,
        )

        # 200 indicates success, no need to check JSON response.
        response.raise_for_status()
