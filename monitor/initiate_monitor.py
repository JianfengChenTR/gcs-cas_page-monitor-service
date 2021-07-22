from asyncio import Future
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import Dict

from blue_green_deployment_check import BlueGreenDeploymentCheck
from properties import property_loader
from request.page_monitor_request import PageMonitorRequest
from util.gcs_logger.gcs_logger import GcsLogger
from util.listeners.aws_sqs_listener import AwsSqsListener
from util.listeners.queue_listener import QueueListener

"""
Run this with environment variable "ENVIRONMENT" set to a value. The corresponding properties-{env}.ini file will be used.
"""

logger: GcsLogger = GcsLogger(__name__)

INTERVAL_TO_CHECK_STATE: int = 60

PAGE_MONITOR_REQUEST_QUEUE_ARN: str = property_loader.get_string_property('page_monitor_request_queue_arn')
PAGE_MONITOR_REQUEST_QUEUE_VISIBILITY_TIMEOUT: int = 300

delivery_listeners: [QueueListener] = {
    AwsSqsListener(
        PAGE_MONITOR_REQUEST_QUEUE_ARN,
        PageMonitorRequest(),
        PAGE_MONITOR_REQUEST_QUEUE_VISIBILITY_TIMEOUT),
}

logger.info(f"Application started")
executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)


class AppRunner:
    def __init__(self, interval: int):
        self._stopped: Event = Event()
        self._interval: int = interval
        self._blue_green_deployment_check: BlueGreenDeploymentCheck = BlueGreenDeploymentCheck()
        self._active_listeners: Dict[AwsSqsListener, Future] = {}

    def run(self) -> None:
        logger.debug(f'Checking for active version')
        self._do_iteration()
        while not self._stopped.wait(self._interval):
            self._do_iteration()

    def _do_iteration(self) -> None:
        is_active: bool = self._blue_green_deployment_check.is_active()
        if is_active:
            if not self._active_listeners:
                logger.debug(f'Starting listeners...')
                for listener in delivery_listeners:
                    listener.is_active = True
                    future: Future = executor.submit(listener)
                    self._active_listeners[listener] = future
                    logger.debug(f'Listener {listener.name} is started')
        else:
            if self._active_listeners:
                logger.debug(f'Shutting down listeners...')
                for listener in self._active_listeners.keys():
                    listener.is_active = False
                as_completed(self._active_listeners.values())
                self._active_listeners.clear()
                logger.debug(f'All listeners are stopped')


AppRunner(INTERVAL_TO_CHECK_STATE).run()
