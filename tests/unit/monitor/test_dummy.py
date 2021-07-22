from gcs_jsonlogger.gcs_logger import GcsLogger

logger: GcsLogger = GcsLogger(__name__)


def test_dummy():
    logger.info(f"Application started")
