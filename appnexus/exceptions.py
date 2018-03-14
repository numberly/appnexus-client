class AppNexusException(Exception):
    """Represents a generic AppNexus Exception"""

    def __init__(self, response=None):
        self.response = response

    def __str__(self):
        if not self.response:
            return "Error with AppNexus API"
        data = self.response.json()["response"]
        error_name = data.get('error_code', data["error_id"])
        description_error = data.get("error", "(indisponible)")
        return "{}: {}".format(error_name, description_error)


class RateExceeded(AppNexusException):
    """Exception raised when the client reached the rate limit"""
    pass


class NoAuth(AppNexusException):
    """Exception raised when the client's authentication expired"""
    pass


class BadCredentials(AppNexusException):
    """Exception raised when wrong credentials are provided"""

    def __str__(self):
        return "You provided bad credentials for the AppNexus API"


__all__ = ["AppNexusException", "RateExceeded", "NoAuth", "BadCredentials"]
