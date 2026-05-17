from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class OBSClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 4455, password: str = ""):
        self._host = host
        self._port = port
        self._password = password
        self._connected = False

    def connect(self) -> bool:
        logger.info("OBS connect stub: %s:%s", self._host, self._port)
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False
        logger.info("OBS disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected
