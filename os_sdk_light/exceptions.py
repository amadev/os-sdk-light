class BaseException(Exception):
    pass


class CannotConnectToCloud(BaseException):

    """Error while gettting endpoint for service.

    Errors like invalid connection configuration, invalid auth,
    no endpoint exists, etc.

    """

    pass


class SchemaError(BaseException):

    """Schema reading related error.

    Errors like no schema file, invalid format, etc.

    """

    pass


class ValidationError(BaseException):

    """Error when input/output does not match correcpoding schema.

    Both request and response could have json schemas, if they does not match
    actual data the exception occured.

    """

    pass
