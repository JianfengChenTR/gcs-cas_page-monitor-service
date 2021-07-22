import time
from typing import Generator, Any

from util.gcs_logger.gcs_logger import GcsLogger
from util.ibm_mq.ibm_mq_client import IbmMqClient
from util.ibm_mq.mq_config import MqConfig
from util.listeners.queue_listener import QueueListener

LOGGER: GcsLogger = GcsLogger(__name__)


class IbmMqListener(QueueListener):
    def __init__(self, mq_config: MqConfig, handler: callable, poll_interval=60):
        super().__init__(f'{self.__class__.__name__} {mq_config}', handler, poll_interval)
        self._mq_config: MqConfig = mq_config

    def read_messages(self) -> Generator[Any, None, None]:
        with IbmMqClient(self._mq_config) as queue:
            for message in queue.get_messages():
                LOGGER.info(message)
                yield message
        time.sleep(self._poll_interval)

    def _handle(self, message) -> None:
        self._handler(message)

    def __eq__(self, other):
        return self == other or (self.__class__ == other.__class__ and self.name == other.name)

    def __hash__(self):
        return hash(self.name)
