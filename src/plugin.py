import asyncio
import logging

logger = logging.getLogger(__name__)

class Plugin(object):
    """Base class that each plugin must inherit from. within this class
    you must define the methods that all of your plugins must implement
    """

    def __init__(self):
        self.name = None
        self.description = None

    # methods to be implemented by inherited classes
    def ping(self) -> str:
        raise NotImplementedError

    def loop(self, argument) -> None:
        raise NotImplementedError