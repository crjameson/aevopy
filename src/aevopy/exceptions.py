class AevoException(Exception):
    """Base class for exceptions in this module."""
    pass

class ConfigurationException(AevoException):
    """Base class for exceptions in this module."""
    pass

class UnauthorizedException(AevoException):
    """Exception raised for 401 Unauthorized status code."""
    def __init__(self, message="UNAUTHORIZED"):
        super().__init__(message)

class RateLimitException(AevoException):
    """Exception raised for 401 Unauthorized status code."""
    def __init__(self, message="RATE_LIMIT_EXCEEDED."):
        super().__init__(message)

class ServerErrorException(AevoException):
    """Exception raised for 500 status code."""
    def __init__(self, message="INTERNAL_ERROR"):
        super().__init__(message)