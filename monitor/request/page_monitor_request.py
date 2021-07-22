from util.gcs_logger.gcs_logger import GcsLogger


class PageMonitorRequest:
    def __init__(self):
        self._logger: GcsLogger = GcsLogger(__name__)
        self._logger.info("to be implemented")
