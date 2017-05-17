import unittest
from unittest.mock import patch

# import os
# import sys
# current_dir = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, current_dir)
# sys.path.insert(1, os.path.join(current_dir, 'toripchanger'))

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
