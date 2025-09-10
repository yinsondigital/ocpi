from enum import Enum


class ConnectionStatus(str, Enum):
    # Party is connected.
    connected = 'CONNECTED'
    # Party is currently not connected
    offline = 'OFFLINE'  # nosec
    # Connection to this party is planned, but has never been connected.
    planned = 'PLANNED'  # nosec
    # Party is now longer active, will never connect anymore.
    suspended = 'SUSPENDED'  # nosec
