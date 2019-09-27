[![Build Status](https://travis-ci.org/DusanMadar/TorIpChanger.svg?branch=master)](https://travis-ci.org/DusanMadar/TorIpChanger)
[![Coverage Status](https://coveralls.io/repos/github/DusanMadar/TorIpChanger/badge.svg?branch=master)](https://coveralls.io/github/DusanMadar/TorIpChanger?branch=master)
[![PyPI version](https://badge.fury.io/py/toripchanger.svg)](https://badge.fury.io/py/toripchanger)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


# TorIpChanger
A simple workaround for [Tor IP changing behavior](https://stem.torproject.org/faq.html#how-do-i-request-a-new-identity-from-tor):

> An important thing to note is that a new circuit does not necessarily mean a new IP address. Paths are randomly selected based on heuristics like speed and stability. There are only so many large exits in the Tor network, so it's not uncommon to reuse an exit you have had previously.

## Installation
```bash
pip install toripchanger
```

TorIpChanger assumes you have installed and setup Tor and Privoxy, for example following steps mentioned in these tutorials:

* [A step-by-step guide how to use Python with Tor and Privoxy](https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b)
* [Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
  * [Alternative link (Gist)](https://gist.github.com/KhepryQuixote/46cf4f3b999d7f658853) for "Crawling anonymously with Tor in Python"

Or, when using Docker, simply use https://github.com/dperson/torproxy.


## Usage
### Basic examples
With TorIpChanger you can define how often a Tor IP can be reused:
```python
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

#### Use `0.0.0.0` as control address
Set `ControlPort` to `0.0.0.0:9051` in your `torrc` file  and set `tor_address` when initializing TorIpChanger
```python
from toripchanger import TorIpChanger

tor_ip_changer = TorIpChanger(tor_address="172.17.0.2")
current_ip = tor_ip_changer.get_new_ip()
```

Though, Tor is not very happy about it (and rightly so) and will warn you
>You have a ControlPort set to accept connections from a non-local address. This means that programs not running on your computer can reconfigure your Tor. That's pretty bad, since the controller protocol isn't encrypted! Maybe you should just listen on 127.0.0.1 and use a tool like stunnel or ssh to encrypt remote connections to your control port.

Also, you have to set either `CookieAuthentication` or `HashedControlPassword` otherwise `ControlPort` will be closed
>You have a ControlPort set to accept unauthenticated connections from a non-local address. This means that programs not running on your computer can reconfigure your Tor, without even having to guess a password. That's so bad that I'm closing your ControlPort for you. If you need to control your Tor remotely, try enabling authentication and using a tool like stunnel or ssh to encrypt remote access.

Please note `ControlListenAddress` config is **OBSOLETE** and Tor (tested with 0.3.3.7) will ignore it and log the following message
> ```
> [warn] Skipping obsolete configuration option 'ControlListenAddress'
> ```

While the config itself is obsolte, its [documentation](https://people.torproject.org/~sysrqb/webwml/docs/tor-manual.html.en#ControlListenAddress) (**not the official documentation!**) concerning the risks related to exposing `ControlPort` on `0.0.0.0` is still valid
> We strongly recommend that you leave this alone unless you know what you’re doing, since giving attackers access to your control listener is really dangerous.

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
  2. start `toripchanger_server` (on the same host where Tor runs)
  3. expose the port `toripchanger_server` runs on to Docker host (or other containers)
  4. test changing IP works, e.g. `curl http://localhost:8080/changeip/`
