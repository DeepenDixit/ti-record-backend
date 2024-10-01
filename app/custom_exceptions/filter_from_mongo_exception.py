class MongoDBConnectionError(Exception):
    """MongoDB connection error exception"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MongoDBOperationError(Exception):
    """MongoDB operation error exception"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
