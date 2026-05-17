from __future__ import annotations

import logging

import obsws_python as obs

logger = logging.getLogger(__name__)


class OBSClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 4455, password: str = ""):
        self._host = host
        self._port = port
        self._password = password
        self._client: obs.ReqClient | None = None

    def connect(self, host: str = "", port: int = 0) -> bool:
        if host:
            self._host = host
        if port:
            self._port = port
        try:
            self._client = obs.ReqClient(
                host=self._host,
                port=self._port,
                password=self._password,
                timeout=3,
            )
            version = self._client.get_version()
            logger.info(
                "OBS connected to %s:%d — %s",
                self._host,
                self._port,
                version.obs_version,
            )
            return True
        except Exception as e:
            logger.error("OBS connection failed: %s", e)
            self._client = None
            return False

    def disconnect(self) -> None:
        if self._client is not None:
            try:
                pass
            except Exception:
                pass
            self._client = None
            logger.info("OBS disconnected")

    @property
    def is_connected(self) -> bool:
        return self._client is not None
