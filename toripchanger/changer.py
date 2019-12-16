import ipaddress
from time import sleep

from requests import get
from requests.exceptions import RequestException
from stem import Signal
from stem.control import Controller

from toripchanger.exceptions import TorIpError

# Default settings.
REUSE_THRESHOLD = 1
LOCAL_HTTP_PROXY = "127.0.0.1:8118"
NEW_IP_MAX_ATTEMPTS = 10
TOR_PASSWORD = ""
TOR_ADDRESS = "127.0.0.1"
TOR_PORT = 9051
POST_NEW_IP_SLEEP = 0.5


# Service to get current IP.
ICANHAZIP = "http://icanhazip.com/"


class TorIpChanger:
    def __init__(
        self,
        reuse_threshold=REUSE_THRESHOLD,
        local_http_proxy=LOCAL_HTTP_PROXY,
        tor_password=TOR_PASSWORD,
        tor_address=TOR_ADDRESS,
        tor_port=TOR_PORT,
        new_ip_max_attempts=NEW_IP_MAX_ATTEMPTS,
        post_new_ip_sleep=POST_NEW_IP_SLEEP,
    ):
        """
        TorIpChanger - make sure requesting a new Tor IP address really does
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
        :argument local_http_proxy: local proxy IP and port
        :type local_http_proxy: str
        :argument tor_password: Tor password
        :type tor_password: str
        :argument tor_address: IP address of the Tor controller
        :type tor_address: str
        :argument tor_port: port number of the Tor controller
        :type tor_port: int
        :argument new_ip_max_attempts: get new IP attemps limit
        :type new_ip_max_attempts: int
        :argument post_new_ip_sleep: how long to wait after requesting a new IP
        :type post_new_ip_sleep: float
        """
        self.reuse_threshold = reuse_threshold
        self.local_http_proxy = local_http_proxy
        self.tor_password = tor_password
        self.tor_address = tor_address
        self.tor_port = tor_port
        self.new_ip_max_attempts = new_ip_max_attempts
        self.post_new_ip_sleep = post_new_ip_sleep

        self.used_ips = []  # We cannot use set() because order matters.

    @property
    def real_ip(self):
        """
        The actual public IP of this host.
        """
        if not hasattr(self, "_real_ip"):
            response = get(ICANHAZIP)
            self._real_ip = self._get_response_text(response)

        return self._real_ip

    def get_current_ip(self):
        """
        Get the current IP Tor is using.

        :returns str
        :raises TorIpError
        """
        response = get(ICANHAZIP, proxies={"http": self.local_http_proxy})

        if response.ok:
            return self._get_response_text(response)

        raise TorIpError("Failed to get the current Tor IP")

    def get_new_ip(self):
        """
        Try to obtain new a usable TOR IP.

        :returns bool
        :raises TorIpError
        """
        attempts = 0

        while True:
            if attempts == self.new_ip_max_attempts:
                raise TorIpError("Failed to obtain a new usable Tor IP")

            attempts += 1

            try:
                current_ip = self.get_current_ip()
            except (RequestException, TorIpError):
                self._obtain_new_ip()
                continue

            if not self._ip_is_usable(current_ip):
                self._obtain_new_ip()
                continue

            self._manage_used_ips(current_ip)
            break

        return current_ip

    def _get_response_text(self, response):
        return response.text.strip()

    def _ip_is_safe(self, current_ip):
        """
        Check if it's safe to (re-)use the current IP.

        :argument current_ip: current Tor IP
        :type current_ip: str

        :returns bool
        """
        return current_ip not in self.used_ips

    def _ip_is_usable(self, current_ip):
        """
        Check if the current Tor's IP is usable.

        :argument current_ip: current Tor IP
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
        if not self._ip_is_safe(current_ip):
            return False

        return True

    def _manage_used_ips(self, current_ip):
        """
        Handle registering and releasing used Tor IPs.

        :argument current_ip: current Tor IP
        :type current_ip: str
        """
        # Register current IP.
        self.used_ips.append(current_ip)

        # Release the oldest registred IP.
        if self.reuse_threshold:
            if len(self.used_ips) > self.reuse_threshold:
                del self.used_ips[0]

    def _obtain_new_ip(self):
        """
        Change Tor's IP.
        """
        with Controller.from_port(
            address=self.tor_address, port=self.tor_port
        ) as controller:
            controller.authenticate(password=self.tor_password)
            controller.signal(Signal.NEWNYM)

        # Wait till the IP 'settles in'.
        sleep(self.post_new_ip_sleep)
