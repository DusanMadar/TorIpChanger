import unittest
from unittest.mock import patch

from toripchanger.utils import get
from toripchanger.config import LOCAL_HTTP_PROXY


class TestGet(unittest.TestCase):
    @patch('toripchanger.utils.requests.get')
    def test_get(self, mock_get):
        """Test proxies are injected to the 'requests.get' call."""
        get('http://www.texturl.com')

        mock_get.assert_called_once_with(
            'http://www.texturl.com',
            proxies=LOCAL_HTTP_PROXY
        )


if __name__ == '__main__':
    unittest.main()
