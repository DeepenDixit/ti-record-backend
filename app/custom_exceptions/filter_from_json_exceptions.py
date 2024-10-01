class JSONFileNotFoundError(Exception):
    """JSON file not found exception"""

    def __init__(self, message: str):
        super().__init__(message)
