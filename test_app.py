from __future__ import annotations

import threading
import unittest
from unittest import mock

import app


class NetworkKeepaliveTests(unittest.TestCase):
    @mock.patch("app.socket.socket")
    def test_send_network_keepalive_sends_dns_packet(self, socket_cls: mock.Mock) -> None:
        sock = socket_cls.return_value.__enter__.return_value

        app.send_network_keepalive()

        socket_cls.assert_called_once_with(app.socket.AF_INET, app.socket.SOCK_DGRAM)
        packet, target = sock.sendto.call_args.args
        self.assertGreater(len(packet), 12)
        self.assertEqual(target, app.KEEPALIVE_TARGET)

    @mock.patch("app.send_network_keepalive")
    def test_keepalive_loop_stops_after_signal(self, send: mock.Mock) -> None:
        stop = threading.Event()
        stop.set()

        app.network_keepalive_loop(stop)

        send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
