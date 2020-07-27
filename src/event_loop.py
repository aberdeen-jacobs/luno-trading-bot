import time
import asyncio
import logging
from plugin_handler import PluginHandler
from data_provider import DataProvider

logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()

class EventLoop:
    """Event loops and other routines are defined here"""

    def __init__(self):
        # Initialize the data provider for internal communication
        self.data_provider = DataProvider()

        # Initialize the plugin handler for managing plugins
        self.plugin_handler = PluginHandler('plugins', self.data_provider)

    async def plugins_runner(self):
        """Repeat the execution of all enabled Plugins"""

        while True:
            self.plugin_handler.update()
            await self.plugin_handler.invoke_callback('main')
            await asyncio.sleep(1)
            #logger.info(self.plugin_handler.enabled_plugins)

    async def data_provider_loop(self):
        """IMPLEMENT THIS CORRECTLY"""
        
        while True:
            logger.info('Broadcasted first object')
            await self.data_provider.broadcast({'time': time.strftime("%H:%M:%S", time.localtime()), 'msg': 'first update'})
            await asyncio.sleep(6)
            plugin = self.plugin_handler.get_plugin_obj('plugins.identity')
            logger.info('Broadcasted second object')
            await self.data_provider.broadcast({'time': time.strftime("%H:%M:%S", time.localtime()), 'msg': 'second update'})
            await asyncio.sleep(6)
            self.plugin_handler.enable(plugin)
            logger.info('Broadcasted third object')
            await self.data_provider.broadcast({'time': time.strftime("%H:%M:%S", time.localtime()), 'msg': 'third update'})
            await asyncio.sleep(6)