class PytailorBaseError(Exception):
    pass


class BackendResponseError(PytailorBaseError):
    pass


class ExistsBackendError(PytailorBaseError):
    pass
