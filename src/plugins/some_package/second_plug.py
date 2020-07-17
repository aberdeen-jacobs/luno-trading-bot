import asyncio
import logging

from plugin import Plugin

logger = logging.getLogger(__name__)

class SecondPlugin(Plugin):
    """This plugin is just the identity function: it returns the argument"""
    def __init__(self):
        super().__init__()
        self.name = __name__
        self.description = 'Identity function'

    def ping(self) -> str:
        return 'Pong!'

    def loop(self, argument) -> None:
        logger.info('Event loop of plugin: {}'.format(__name__))
        logger.info(' '.join(argument))