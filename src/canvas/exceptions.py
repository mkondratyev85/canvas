class CanvasException(Exception):
    """Basic exception for errors raised by Canvas."""

    def __init__(self, msg):
        super(CanvasException, self).__init__(msg)

class CanvasError(CanvasException):
    pass

