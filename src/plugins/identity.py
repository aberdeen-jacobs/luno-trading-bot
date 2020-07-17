import asyncio
import logging
import time

from plugin import Plugin

logger = logging.getLogger(__name__)

class Identity(Plugin):
    """This plugin is just the identity function: it returns the argument"""
    def __init__(self):
        super().__init__()
        self.name = __name__
        self.description = 'Identity function'

    def ping(self) -> str:
        return 'Pong!'

    def loop(self, argument) -> None:
        logger.info('Event loop of plugin: {}'.format(__name__))
        logger.info(argument)
        #logger.info('PAUZING')
        #time.sleep(5)
    
    def run(self, string: str):
        logger.info('I can also invoke callbacks on specific functions')