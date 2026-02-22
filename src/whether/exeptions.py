
class InvalidCoordinateError(ValueError):
    """Некорректные координаты WGS84."""


class InvalidTimezoneError(ValueError):
    """Некорректное имя часового пояса IANA."""

class InvalidDateFormatError(ValueError):
    """Некорректный формат даты (ожидается YYYY-MM-DD)."""
