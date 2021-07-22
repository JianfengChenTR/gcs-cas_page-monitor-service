import logging
import uuid

from gcs_jsonlogger.gcs_log_formatter import GcsLogFormatter

END_USER_EVENT_TYPE = 'END_USER'
EVENT_TYPE_TRACING_LOG_FIELD = 'event_type'


class GcsLogger:

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger('com.tr.gcs.' + logger_name)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = GcsLogFormatter()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        self._logging_context: dict = {}
        self._logging_tracing: dict = {}
        self._logging_extra: dict = {'contextMap': self._logging_context, 'tracing': self._logging_tracing}
        self.logger_adapter = logging.LoggerAdapter(logger=self.logger, extra=self._logging_extra)

    def set_correlation_id(self, correlation_id: uuid.UUID) -> None:
        """
        Sets the tracing correlation_id field which is used to correlate log events together.
        This is an indexed field in Datadog.
        Parameters
        ----------
        correlation_id: uuid.UUID
        """
        self._logging_tracing['correlation_id'] = str(correlation_id)

    def set_event_type(self, event_type: str) -> None:
        """
        Sets the tracing event_type field which is used to define the type of logging event.  For logs to be displayed by default to 'end users' in Content Watch, set this to 'END_USER'.
        This is an indexed field in Datadog.
        Parameters
        ----------
        event_type: str
        """
        self._logging_tracing[EVENT_TYPE_TRACING_LOG_FIELD] = event_type

    def set_error_id(self, error_id: uuid.UUID) -> None:
        """
        Sets the tracing error_id field which is used for error events in APIs.
        This allows the API error response to include the error id which can then be used for debugging logs in the service.
        This is an indexed field in Datadog.
        Parameters
        ----------
        error_id: uuid.UUID
        """
        self._logging_tracing['error_id'] = str(error_id)

    def add_context(self, key: str, value: str) -> None:
        """
        Adds a key/value pair to the logging 'context' object.  Once set, this will be included in all log events until removed.
        Parameters
        ----------
        key: str
        value: str
        """
        self._logging_context[key] = value

    def remove_context(self, key: str) -> None:
        """
        Removes a key/value pair from the logging 'context' object.
        Parameters
        ----------
        key: str
        """
        if key in self._logging_context:
            del self._logging_context[key]

    def clear_context(self) -> None:
        """
        Removes all key/value pairs from the logging 'context' object.
        """
        self._logging_context.clear()

    def add_tracing(self, key: str, value: str) -> None:
        """
        Adds a key/value pair to the logging 'tracing' object.  Once set, this will be included in all log events until removed.
        Parameters
        ----------
        key: str
        value: str
        """
        self._logging_tracing[key] = value

    def remove_tracing(self, key: str) -> None:
        """
        Removes a key/value pair from the logging 'tracing' object.
        Parameters
        ----------
        key: str
        """
        if key in self._logging_tracing:
            del self._logging_tracing[key]

    def clear_tracing(self) -> None:
        """
        Removes all key/value pairs from the logging 'tracing' object.
        """
        self._logging_tracing.clear()

    def clear_all(self) -> None:
        """
        Removes all the fields from the logging 'context' and 'tracing' objects.
        """
        self.clear_context()
        self.clear_tracing()

    def debug(self, message: str) -> None:
        """
        Writes a log DEBUG event.
        Parameters
        ----------
        message: str
        """
        self.logger_adapter.debug(message)

    def info(self, message: str, end_user: bool = False) -> None:
        """
        Writes a log INFO event.
        Parameters
        ----------
        message: str
        end_user: bool
            If True, this single log event gets logged with the tracing event_type field of 'END_USER'.
        """
        if end_user:
            self.set_event_type(END_USER_EVENT_TYPE)
        self.logger_adapter.info(message)
        if end_user:
            self.remove_tracing(EVENT_TYPE_TRACING_LOG_FIELD)

    def warn(self, message: str, exc_info: bool = False, end_user: bool = False) -> None:
        """
        Writes a log WARN event.
        Parameters
        ----------
        message: str
        exc_info: bool
            If True, the exception info and stack trace is included in the log event.
        end_user: bool
            If True, this single log event gets logged with the tracing event_type field of 'END_USER'.
        """
        if end_user:
            self.set_event_type(END_USER_EVENT_TYPE)
        self.logger_adapter.warning(message, exc_info=exc_info)
        if end_user:
            self.remove_tracing(EVENT_TYPE_TRACING_LOG_FIELD)

    def exception(self, message: str, exc_info: bool = True, end_user: bool = False) -> None:
        """
        Writes a log ERROR event.
        Parameters
        ----------
        message: str
        exc_info: bool
            If True, the exception info and stack trace is included in the log event.
        end_user: bool
            If True, this single log event gets logged with the tracing event_type field of 'END_USER'.
        """
        if end_user:
            self.set_event_type(END_USER_EVENT_TYPE)
        self.logger_adapter.exception(message, exc_info=exc_info)
        if end_user:
            self.remove_tracing(EVENT_TYPE_TRACING_LOG_FIELD)
