import ipaddress
from time import sleep

import requests
from stem import Signal
from stem.control import Controller

from config import (
    NEW_IP_MAX_ATTEMPTS,
    TOR_PASSWORD,
    TOR_PORT,
)
from utils import get as get_with_tor


ICANHAZIP = 'http://icanhazip.com/'


class TorIpError(Exception):
    pass


class TorIpChanger(object):
    def __init__(self, reuse_threshold=1):
        """TorIpChanger - make sure requesting a new Tor IP address really does
        return a new (different) IP.

        The 'reuse_threshold' argument specifies the number of unique Tor IPs
        kept in the 'used_ips' list which works as a FIFO queue.

        When 'reuse_threshold' is set to 0 then none of the already used Tor IP
        addresses can be reused.
        When 'reuse_threshold' is set to 1 (which is default) then the current
        Tor IP address can be reused after one other IP was used.
        If 'reuse_threshold' is set to, for example, 5 then the current Tor IP
        address can be reused after 5 other Tor IPs were used.

        :argument reuse_threshold: IPs to use before reusing the current one
        :type reuse_threshold: int

        :returns bool
        """
        self.reuse_threshold = reuse_threshold
        self.used_ips = []

        self._real_ip = None

    @property
    def real_ip(self):
        """The actual public IP address of this computer."""
        if self._real_ip is None:
            response = requests.get(ICANHAZIP)
            self._real_ip = self._get_response_text(response)

        return self._real_ip

    def get_current_ip(self):
        """Get the current IP address TOR is using.

        :returns str
        :raises TorIpError
        """
        response = get_with_tor(ICANHAZIP)

        if response.ok:
            return self._get_response_text(response)

        raise TorIpError('Failed to get the current TOR IP address')

    def get_new_ip(self):
        """Try to obtain new a usable TOR IP.

        :returns bool
        :raises TorIpError
        """
        attempts = 0

        while True:
            if attempts == NEW_IP_MAX_ATTEMPTS:
                raise TorIpError('Failed to obtain a new usable TOR IP')

            attempts += 1

            try:
                current_ip = self.get_current_ip()
            except TorIpError as exc:
                self._obtain_new_ip()
                continue

            ip_usable = self._ip_is_usable(current_ip)
            if not ip_usable:
                self._obtain_new_ip()
                continue

            self._manage_used_ips(current_ip)
            break

        return current_ip

    def _get_response_text(self, response):
        return response.text.strip()

    def _ip_is_usable(self, current_ip):
        """Check if the current TOR's IP address is usable.

        :argument current_ip: current TOR IP address
        :type current_ip: str

        :returns bool
        """
        # Consider IP addresses only.
        try:
            ipaddress.ip_address(current_ip)
        except ValueError:
            return False

        # Never use real IP.
        if current_ip == self.real_ip:
            return False

        # Do dot allow IP reuse.
        if current_ip in self.used_ips:
            return False

        return True

    def _manage_used_ips(self, current_ip):
        """Handle registering and releasing used Tor IPs.

        :argument current_ip: current TOR IP address
        :type current_ip: str
        """
        # Register current IP.
        self.used_ips.append(current_ip)

        # Release the oldest registred IP.
        if self.reuse_threshold:
            if len(self.used_ips) > self.reuse_threshold:
                del self.used_ips[0]

    def _obtain_new_ip(self):
        """Change TOR's IP"""
        with Controller.from_port(port=TOR_PORT) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)

        # Wait till the IP 'settles in'.
        sleep(0.5)
