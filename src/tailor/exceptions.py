class PytailorBaseError(Exception):
    pass


class BackendResponseError(PytailorBaseError):
    pass


class BackendResourceError(PytailorBaseError):
    pass
