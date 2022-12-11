class HTTPStatus(Exception):
    """Exception raised for an unexpected HTTP status code from the server.

    Attributes:
        status_code: The HTTP status code that was returned by the server.
    """

    def __init__(self, status_code):
        """Initialize the HTTPStatus exception.

        Args:
            status_code: The HTTP status code that was returned by the server.
        """
        self.status_code = status_code

    def __str__(self):
        """Return a string representation of the HTTPStatus exception."""
        return f"Unexpected status code from server: {self.status_code}"
