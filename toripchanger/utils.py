from functools import wraps

import requests

from config import LOCAL_HTTP_PROXY


def proxied(f):
    """Injects the TOR/Privoxy proxy settings to kwargs"""
    @wraps(f)
    def with_proxy(*args, **kwargs):
        kwargs['proxies'] = LOCAL_HTTP_PROXY
        return f(*args, **kwargs)

    return with_proxy


@proxied
def get(*args, **kwargs):
    """A simple`reqeuests.get` wrapper."""
    return requests.get(*args, **kwargs)
