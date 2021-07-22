from threading import Event, Thread

from util.gcs_logger.gcs_logger import GcsLogger

logger: GcsLogger = GcsLogger(__name__)


class MessageVisibilityWatchDog(Thread):

    def __init__(self, message, visibility_timeout: int, check_interval: float = 120):
        super().__init__(name=f'MessageVisibilityWatchDog-{message.queue_url}')
        self._message = message
        self._visibility_timeout: int = visibility_timeout
        self._stopped: Event = Event()
        self._check_interval: float = check_interval

    def run(self) -> None:
        logger.debug(f'WatchDog is started')
        while not self._stopped.wait(self._check_interval):
            logger.debug(f'Updated visibility timeout to {self._visibility_timeout} for {self._message} ')
            self._message.change_visibility(VisibilityTimeout=self._visibility_timeout)
        logger.debug(f'WatchDog is stopped')

    def stop(self):
        self._stopped.set()
        logger.debug(f'WatchDog is being stopped...')
