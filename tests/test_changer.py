import unittest
from unittest.mock import patch, Mock

from stem import Signal

import os
import sys
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(1, os.path.join(current_dir, 'toripchanger'))

from toripchanger.changer import ICANHAZIP, TorIpChanger, TorIpError
from toripchanger import config


class TestTorIpChanger(unittest.TestCase):
    def test_init(self):
        """Test that 'TorIpChanger' init sets expected (default) attributes."""
        tor_ip_changer = TorIpChanger()

        self.assertEqual(tor_ip_changer.reuse_threshold, 1)
        self.assertFalse(tor_ip_changer.used_ips)

    def test_init_reuse_threshold(self):
        """Test that 'TorIpChanger' init sets reuse_threshold when proxied."""
        tor_ip_changer = TorIpChanger(5)

        self.assertEqual(tor_ip_changer.reuse_threshold, 5)

    @patch('toripchanger.changer.requests.get')
    @patch('toripchanger.changer.TorIpChanger._get_response_text')
    def test_real_ip(self, mock_get_response_text, mock_get):
        """Test that 'real_ip' is obtained by normal 'request.get',
        i.e. without routing trafic through Tor/Privoxy."""
        mock_response = Mock()
        mock_get.return_value = mock_response

        tor_ip_changer = TorIpChanger()
        tor_ip_changer.real_ip

        mock_get.assert_called_once_with(ICANHAZIP)
        mock_get_response_text.assert_called_once_with(mock_response)

    @patch('toripchanger.changer.get_with_tor')
    @patch('toripchanger.changer.TorIpChanger._get_response_text')
    def test_current_ip(self, mock_get_response_text, mock_get_with_tor):
        """Test that 'get_current_ip' is obtained by wrapped 'request.get'
        i.e. routing trafic through Tor/Privoxy."""
        mock_get_response_text.return_value = '9.9.9.9'

        tor_ip_changer = TorIpChanger()
        current_ip = tor_ip_changer.get_current_ip()

        self.assertEqual(
            current_ip,
            mock_get_response_text.return_value
        )

        mock_get_with_tor.assert_called_once_with(ICANHAZIP)

    @patch('toripchanger.changer.get_with_tor')
    def test_current_ip_exception(self, mock_get_with_tor):
        """Test that 'get_current_ip' raises TorIpError when an IP isn't
        returned."""
        mock_response = Mock()
        mock_response.ok = False
        mock_get_with_tor.return_value = mock_response

        tor_ip_changer = TorIpChanger()

        with self.assertRaises(TorIpError):
            tor_ip_changer.get_current_ip()

    @patch('toripchanger.changer.TorIpChanger.get_current_ip')
    @patch('toripchanger.changer.TorIpChanger._obtain_new_ip')
    def test_get_new_ip_current_ip_failed(
        self, mock_obtain_new_ip, mock_get_current_ip
    ):
        """Test that 'get_new_ip' attempts to get a new IP only the limited
        number of times when 'get_current_ip' keeps failing."""
        mock_get_current_ip.side_effect = TorIpError

        tor_ip_changer = TorIpChanger()

        with self.assertRaises(TorIpError):
            tor_ip_changer.get_new_ip()

        self.assertEqual(
            mock_obtain_new_ip.call_count, config.NEW_IP_MAX_ATTEMPTS
        )
        self.assertEqual(
            mock_get_current_ip.call_count, config.NEW_IP_MAX_ATTEMPTS
        )

    @patch('toripchanger.changer.TorIpChanger.get_current_ip')
    @patch('toripchanger.changer.TorIpChanger._obtain_new_ip')
    @patch('toripchanger.changer.TorIpChanger._ip_is_usable')
    def test_get_new_ip_ip_is_usable_failed(
        self, mock_ip_is_usable, mock_obtain_new_ip, mock_get_current_ip
    ):
        """Test that 'get_new_ip' attempts to get a new IP only the limited
        number of times when '_ip_is_usable' keeps returning the same IP."""
        mock_get_current_ip.return_value = '1.1.1.1'
        mock_ip_is_usable.return_value = False

        tor_ip_changer = TorIpChanger()
        tor_ip_changer.used_ips = ['1.1.1.1']

        with self.assertRaises(TorIpError):
            tor_ip_changer.get_new_ip()

        self.assertEqual(
            mock_obtain_new_ip.call_count, config.NEW_IP_MAX_ATTEMPTS
        )
        self.assertEqual(
            mock_get_current_ip.call_count, config.NEW_IP_MAX_ATTEMPTS
        )
        self.assertEqual(
            mock_ip_is_usable.call_count, config.NEW_IP_MAX_ATTEMPTS
        )

    @patch('toripchanger.changer.TorIpChanger.get_current_ip')
    @patch('toripchanger.changer.TorIpChanger._obtain_new_ip')
    def test_get_new_ip_success(self, mock_obtain_new_ip, mock_get_current_ip):
        """Test that 'get_new_ip' gets a new usable Tor IP address on the
        third attempt."""
        mock_get_current_ip.side_effect = [
            '1.1.1.1',
            None,
            '2.2.2.2',
        ]

        tor_ip_changer = TorIpChanger()
        tor_ip_changer.used_ips = ['1.1.1.1']

        new_ip = tor_ip_changer.get_new_ip()

        self.assertEqual(new_ip, '2.2.2.2')
        self.assertEqual([new_ip], tor_ip_changer.used_ips)
        self.assertEqual(mock_obtain_new_ip.call_count, 2)
        self.assertEqual(mock_get_current_ip.call_count, 3)

    def test_get_response_text(self):
        """Test that '_get_response_text' accesses and strips response's text
        property."""
        mock_response = Mock()
        mock_response.text = ' 8.8.8.8\n'

        tor_ip_changer = TorIpChanger()
        response = tor_ip_changer._get_response_text(mock_response)

        self.assertEqual(response, '8.8.8.8')

    def test_ip_is_usable_invalid_ip(self):
        """Test that '_ip_is_usable' returns False for an invalid IP."""
        tor_ip_changer = TorIpChanger()

        ip_usable = tor_ip_changer._ip_is_usable('not-an-ip')
        self.assertFalse(ip_usable)

    def test_ip_is_usable_real_ip(self):
        """Test that '_ip_is_usable' returns False for the actual real IP."""
        tor_ip_changer = TorIpChanger()
        tor_ip_changer._real_ip = '0.0.0.0'

        ip_usable = tor_ip_changer._ip_is_usable('0.0.0.0')
        self.assertFalse(ip_usable)

    def test_ip_is_usable_used_ip(self):
        """Test that '_ip_is_usable' returns False for an already used IP."""
        tor_ip_changer = TorIpChanger()
        tor_ip_changer._real_ip = '0.0.0.0'
        tor_ip_changer.used_ips = ['1.1.1.1']

        ip_usable = tor_ip_changer._ip_is_usable('1.1.1.1')
        self.assertFalse(ip_usable)

    def test_ip_is_usable_valid_ip(self):
        """Test that '_ip_is_usable' returns True for a valid IP."""
        tor_ip_changer = TorIpChanger()
        tor_ip_changer._real_ip = '0.0.0.0'

        ip_usable = tor_ip_changer._ip_is_usable('1.1.1.1')
        self.assertTrue(ip_usable)

    def test_manage_used_ips_registers_ip(self):
        """Test that '_manage_used_ips' successfully registers current IP."""
        tor_ip_changer = TorIpChanger()

        current_ip = '1.1.1.1'
        tor_ip_changer._manage_used_ips(current_ip)

        self.assertEqual([current_ip], tor_ip_changer.used_ips)

    def test_manage_usable_ips_releases_used_ip(self):
        """Test that '_manage_used_ips' successfully releases an used IP."""
        tor_ip_changer = TorIpChanger()
        tor_ip_changer.used_ips = ['1.1.1.1']

        current_ip = '2.2.2.2'
        tor_ip_changer._manage_used_ips(current_ip)

        self.assertEqual([current_ip], tor_ip_changer.used_ips)

    def test_manage_used_ips_releases_oldest_used_ip(self):
        """Test that '_manage_used_ips' successfully releases oldest used IP."""
        tor_ip_changer = TorIpChanger(3)
        tor_ip_changer._real_ip = '0.0.0.0'
        tor_ip_changer.used_ips = [
            '1.1.1.1',
            '2.2.2.2',
            '3.3.3.3',
        ]

        current_ip = '4.4.4.4'
        expected_used_ips = [
            '2.2.2.2',
            '3.3.3.3',
            current_ip
        ]

        tor_ip_changer._manage_used_ips(current_ip)
        self.assertEqual(tor_ip_changer.used_ips, expected_used_ips)

    @patch('toripchanger.changer.Controller.from_port')
    def test_obtain_new_ip(self, mock_from_port):
        """Test that '_obtain_new_ip' obtains new Tor IP and expected methods
        are called while doing so within the context manager."""
        tor_ip_changer = TorIpChanger()
        tor_ip_changer._obtain_new_ip()

        mock_from_port.assert_any_call(config.TOR_PORT)

        mock_controler = mock_from_port.return_value.__enter__()
        mock_controler.signal.assert_any_call(Signal.NEWNYM)
        mock_controler.authenticate.assert_any_call(config.TOR_PASSWORD)


if __name__ == '__main__':
    unittest.main()
