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

* [Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
* [Selenium, Tor, And You!](http://lyle.smu.edu/~jwadleigh/seltest/)
