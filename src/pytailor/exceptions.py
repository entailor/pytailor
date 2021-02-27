class PytailorBaseError(Exception):
    pass


class BackendResponseError(PytailorBaseError):
    pass


class BackendResourceError(PytailorBaseError):
    pass


class DAGError(PytailorBaseError):
    pass


class ParameterizationError(PytailorBaseError):
    pass


class AuthenticationError(PytailorBaseError):
    pass


class QueryError(PytailorBaseError):
    pass
