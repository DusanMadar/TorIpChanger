[![Build Status](https://travis-ci.org/DusanMadar/TorIpChanger.svg?branch=master)](https://travis-ci.org/DusanMadar/TorIpChanger)
[![Coverage Status](https://coveralls.io/repos/github/DusanMadar/TorIpChanger/badge.svg?branch=master)](https://coveralls.io/github/DusanMadar/TorIpChanger?branch=master)
[![PyPI version](https://badge.fury.io/py/toripchanger.svg)](https://badge.fury.io/py/toripchanger)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


# TorIpChanger

A simple workaround for [Tor IP changing behavior](https://stem.torproject.org/faq.html#how-do-i-request-a-new-identity-from-tor):

> An important thing to note is that a new circuit does not necessarily mean a new IP address. Paths are randomly selected based on heuristics like speed and stability. There are only so many large exits in the Tor network, so it's not uncommon to reuse an exit you have had previously.

## Installation

```
pip install toripchanger
```

TorIpChanger assumes you have installed and setup Tor and Privoxy, for example following steps mentioned in these tutorials:

* [A step-by-step guide how to use Python with Tor and Privoxy](https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b)
* [Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
  * [Alternative link (Gist)](https://gist.github.com/KhepryQuixote/46cf4f3b999d7f658853) for "Crawling anonymously with Tor in Python"


## Usage

### Basic examples

With TorIpChanger you can define how often a Tor IP can be reused:

```
from toripchanger import TorIpChanger

# Tor IP reuse is prohibited.
tor_ip_changer_0 = TorIpChanger(reuse_threshold=0)
current_ip = tor_ip_changer_0.get_new_ip()

# Current Tor IP address can be reused after one other IP was used (default setting).
tor_ip_changer_1 = TorIpChanger(local_http_proxy='127.0.0.1:8888')
current_ip = tor_ip_changer_1 .get_new_ip()

# Current Tor IP address can be reused after 5 other Tor IPs were used.
tor_ip_changer_5 = TorIpChanger(reuse_threshold=5)
current_ip = tor_ip_changer_5.get_new_ip()
```

### Remote Tor control

Sometimes, typically while using Docker, you may want to control a Tor instance
which doesn't run on localhost. To do this, you have two options.

#### Set `ControlListenAddress`

Be aware of the risks concerning this settings described at https://people.torproject.org/~sysrqb/webwml/docs/tor-manual.html.en#ControlListenAddress (not part of the official documentation!):

> We strongly recommend that you leave this alone unless you know what you’re doing, since giving attackers access to your control listener is really dangerous.

Add `ControlListenAddress 0.0.0.0` to your `torrc` file (credits: https://stackoverflow.com/q/45901892/4183498) and set `tor_address` when initializing TorIpChanger

```
from toripchanger import TorIpChanger

tor_ip_changer = TorIpChanger(tor_address="172.17.0.2")
current_ip = tor_ip_changer.get_new_ip()
```


#### Use `toripchanger_server`

`toripchanger_server` script starts a simple web server which allows you to change Tor' IP remotely using an HTTP get request to `/changeip/`. The response body is always

```
{
    "newIp": "1.2.3.4",
    "error": ""
}
```
with an appropriate status (`error` is an empty string when all is good).

Changing Tor' IP may not be instantaneous (especially when combined with a high `reuse_threshold`) and hence your client should use a reasonable timeout (e.g. at least 60s).

`toripchanger_server` takes all arguments required to initialize `TorIpChanger` plus `--server-host` and `--server-port`, for more details see the usage below.

```
usage: toripchanger_server [-h] [--server-host SERVER_HOST]
                           [--server-port SERVER_PORT]
                           [--reuse-threshold REUSE_THRESHOLD]
                           [--local-http-proxy LOCAL_HTTP_PROXY]
                           [--tor-password TOR_PASSWORD]
                           [--tor-address TOR_ADDRESS] [--tor-port TOR_PORT]
                           [--new-ip-max-attempts NEW_IP_MAX_ATTEMPTS]

optional arguments:
  -h, --help            show this help message and exit
  --server-host SERVER_HOST
                        TorIpChanger server host (default: 0.0.0.0)
  --server-port SERVER_PORT
                        TorIpChanger server port (default: 8080)
  --reuse-threshold REUSE_THRESHOLD
                        Number of IPs to use before reusing the current one
                        (default: 1)
  --local-http-proxy LOCAL_HTTP_PROXY
                        Local proxy IP and port (default: 127.0.0.1:8118)
  --tor-password TOR_PASSWORD
                        Tor controller password (default: "")
  --tor-address TOR_ADDRESS
                        IP address of the Tor controller (default: 127.0.0.1)
  --tor-port TOR_PORT   Port number of the Tor controller (default: 9051)
  --new-ip-max-attempts NEW_IP_MAX_ATTEMPTS
                        Get new IP attemps limit (default: 10)
```

To be able to change Tor' IP remotely with `toripchanger_server`:

  1. `pip install toripchanger[server]` in your container
  2. start `toripchanger_server`
  3. expose the port `toripchanger_server` is running on to Docker host (or other containers)
  4. test changing IP works, e.g. `curl http://localhost:8080/changeip/`
