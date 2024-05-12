"""
Checks current machine IP address with and updates DNS A record accordingly.
"""

import argparse
import concurrent.futures
import logging

from porkbunddns import porkbun
from porkbunddns import ipify


parser = argparse.ArgumentParser(
    description="Check current domain A record and update if necessary."
)
parser.add_argument("domain", help="The domain to check and update", type=str)
parser.add_argument("api_key", help="PorkBun API key", type=str)
parser.add_argument("api_secret", help="PorkBun API secret", type=str)
parser.add_argument("--ttl", help="DNS TTL", default=600, type=int)
parser.add_argument("--timeout", help="Request timeout", default=10, type=int)
parser.add_argument("-v", "--verbose", help="Verbose", action="store_true")
args = parser.parse_args()


logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    level=logging.INFO,
    datefmt="[%Y-%m-%dT%H:%M:%S]"
)

logger = logging.getLogger(__name__)

if args.verbose:
    logger.setLevel(logging.DEBUG)

ipify_connector = ipify.IPify(
    timeout=args.timeout,
    verbose=args.verbose
)

porkbun_connector = porkbun.PorkBun(
    api_key=args.api_key,
    api_secret=args.api_secret,
    timeout=args.timeout,
    verbose=args.verbose
)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    record_task = executor.submit(
        porkbun_connector.get_a_record, domain=args.domain)
    current_task = executor.submit(ipify_connector.get_current_ip)

    record = record_task.result()
    current = current_task.result()

logger.debug("Domain: %s, A Record IP: %s", args.domain, record.ip)

logger.debug("Current Machine IP: %s", current.ip)

if current.ip != record.ip:
    logger.debug("Updating %s A record to %s", args.domain, current.ip)
    porkbun_connector.update_a_record(
        domain=args.domain, ip=current.ip, ttl=args.ttl)
else:
    logger.debug("No update required")
