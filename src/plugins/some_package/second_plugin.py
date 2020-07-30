import asyncio
import logging
from plugin import Plugin
from observer import Observer, Observable

logger = logging.getLogger(__name__)
lock = asyncio.Lock()

class SecondPlugin(Plugin):
    """This plugin is just the identity function: it returns the argument"""

    def __init__(self, observable):
        super().__init__(observable)
        self.name = __name__
        self.description = 'Identity function'

    async def algorithm(self):
        logger.info('{} has acces to data: {}'.format(self.name, self.input_data))
        await asyncio.sleep(4)

    async def main(self):
        async with lock:
            await self.algorithm()