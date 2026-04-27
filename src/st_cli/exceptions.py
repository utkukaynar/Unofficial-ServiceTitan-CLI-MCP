"""Exception hierarchy for the ST CLI."""


class STCLIError(Exception):
    """Base exception for all ST CLI errors."""


class ConfigError(STCLIError):
    """Missing or invalid configuration."""


class AuthError(STCLIError):
    """Authentication failure (bad credentials, expired token, etc.)."""


class APIError(STCLIError):
    """Non-success response from the ServiceTitan API."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(404, detail)


class RateLimitError(APIError):
    """Rate limited (429)."""

    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(429, detail)


class DateParseError(STCLIError):
    """Failed to parse a date range string."""
