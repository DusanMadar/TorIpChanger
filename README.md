[![Build Status](https://travis-ci.org/DusanMadar/TorIpChanger.svg?branch=master)](https://travis-ci.org/DusanMadar/TorIpChanger) [![Coverage Status](https://coveralls.io/repos/github/DusanMadar/TorIpChanger/badge.svg?branch=master)](https://coveralls.io/github/DusanMadar/TorIpChanger?branch=master)
[![PyPI version](https://badge.fury.io/py/toripchanger.svg)](https://badge.fury.io/py/toripchanger)


# TorIpChanger

A simple workaround for the [Tor IP chnaging behavior](https://stem.torproject.org/faq.html#how-do-i-request-a-new-identity-from-tor):

> An important thing to note is that a new circuit does not necessarily mean a new IP address. Paths are randomly selected based on heuristics like speed and stability. There are only so many large exits in the Tor network, so it's not uncommon to reuse an exit you have had previously.

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

TorIpChanger assumes you have installed and setup Tor and Privoxy, for example following steps mentioned in these tutorials:

* [A step-by-step guide how to use Python with Tor and Privoxy](https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b)
* [Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
  * [Alternative link (Gist)](https://gist.github.com/KhepryQuixote/46cf4f3b999d7f658853) for "Crawling anonymously with Tor in Python"
* [Selenium, Tor, And You!](http://lyle.smu.edu/~jwadleigh/seltest/)
