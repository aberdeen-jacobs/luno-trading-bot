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

    # Predefined methods
    async def heartbeat(self) -> str:
        return 'Alive!'    

    # Abstract methods
    async def main(self, argument) -> tuple:
        raise NotImplementedError