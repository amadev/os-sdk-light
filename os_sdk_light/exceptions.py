class BaseException(Exception):
    pass


class CannotConnectToCloud(BaseException):
    pass


class SchemaError(BaseException):
    pass


class ValidationError(BaseException):
    pass
