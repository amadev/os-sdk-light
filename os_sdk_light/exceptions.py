class BaseOSLException(Exception):
    pass


class CannotConnectToCloud(BaseOSLException):
    pass


class OSLValidationError(BaseOSLException):
    pass
