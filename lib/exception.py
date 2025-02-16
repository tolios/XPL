class XplError(Exception):
    """Base class for all xpl exceptions."""
    pass

class FileNotFoundError(XplError):
    """Raised when a file does not exist."""
    pass

class UnsupportedFileTypeError(XplError):
    """Raised when an unsupported file type is encountered."""
    pass

class ProcessingError(XplError):
    """Raised when there is an error in processing the file."""
    pass

class AlreadyProcessed(XplError):
    """Raised when the file is already processed."""
    pass
