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


class UnexpectedResponse(BaseException):

    """This happens if client does not get proper response.

    For example, a server returns not expected status like 404, 500.
    Client cannot create session or connection timeouted.

    """

    def __init__(self, message, orig_exception):
        super(UnexpectedResponse, self).__init__(message)
        self.orig_exception = orig_exception

    @property
    def status_code(self):
        if hasattr(self.orig_exception, 'status_code'):
            return self.orig_exception.status_code
        return -1

    @property
    def message(self):
        if hasattr(self.orig_exception, 'message'):
            return self.orig_exception.message
        return ''
