import os
from typing import Optional

from gcs_cpclient.control_plane import ControlPlane, PollingTypes

from properties import property_loader
from util.gcs_logger.gcs_logger import GcsLogger

POLLING_INTERVAL: int = 60

logger: GcsLogger = GcsLogger(__name__)


class BlueGreenDeploymentCheck:
    def __init__(self):
        self._aws_region: str = property_loader.get_string_property('aws.region')
        self._environment: str = property_loader.get_string_property('environment')
        self._version: int = int(os.getenv('VERSION'))
        self._control_plane: Optional[ControlPlane] = None
        logger.info(f'Active version: {self._version}, Active region: {self._aws_region}')
        if self._environment in ['ci', 'qa', 'prod']:
            self._control_plane: ControlPlane = ControlPlane(
                property_loader.get_string_property('service_name'),
                self._environment,
                property_loader.get_string_property('control_plane_auth_token_secret'),
                property_loader.get_string_property('control_plane_domain'),
                property_loader.get_string_property('control_plane_alt_domain'),
            )
            self._control_plane.start_polling_daemon(POLLING_INTERVAL,
                                                     {PollingTypes.ACTIVE_REGION, PollingTypes.ACTIVE_VERSION})

    def is_active(self) -> bool:
        if self._control_plane:
            return (self._control_plane.current_active_region == self._aws_region) and (
                    self._control_plane.current_active_version == self._version)
        else:
            return True
