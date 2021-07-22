import time
from abc import ABC, abstractmethod
from typing import Generator, Any

from util.gcs_logger.gcs_logger import GcsLogger

logger: GcsLogger = GcsLogger(__name__)


class QueueListener(ABC):
    def __init__(self, name: str, handler: callable, poll_interval: int):
        super().__init__()
        self._handler: callable = handler
        self._poll_interval: int = poll_interval
        self.is_active: bool = True
        self.name = name

    @abstractmethod
    def read_messages(self) -> Generator[Any, None, None]:
        pass

    def __call__(self, *args, **kwargs) -> None:
        while self.is_active:
            try:
                for message in self.read_messages():
                    logger.debug(f'Message received: {message}')
                    try:
                        self._handle(message)
                    except Exception as e:
                        logger.exception(f'An error has occurred while processing message: {message}. {str(e)}', end_user=True)
            except Exception as e:
                logger.exception(f'{self.name} has been failed: {str(e)}', exc_info=True, end_user=True)
                time.sleep(60)
        logger.debug(f'{self.name} is shut down')

    @abstractmethod
    def _handle(self, message) -> None:
        pass

    def __eq__(self, other):
        return self == other or (self.__class__ == other.__class__ and self.name == other.name)

    def __hash__(self):
        return hash(self.name)
