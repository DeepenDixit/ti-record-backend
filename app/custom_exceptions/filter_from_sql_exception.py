class SQLConnectionError(Exception):
    """SQL connection error exception"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SQLOperationError(Exception):
    """SQL operation error exception"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
