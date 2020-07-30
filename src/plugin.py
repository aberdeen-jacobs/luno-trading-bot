import asyncio
import logging
from observer import Observer
from data_provider import DataProvider

logger = logging.getLogger(__name__)

class Plugin(Observer):
    """Generic Plugin base class"""

    def __init__(self, data_sink: DataProvider):
        self.name = None
        self.description = None
        self.input_data = None
        self.output_data = None
        self.data_sink = data_sink
        self.is_running = False

    # Predefined methods
    async def heartbeat(self) -> bool:
        """Simple indicator function for checking whether the plugin
        is responsive

        :return: True when alive
        :rtype: bool
        """
        
        return True

    async def update(self):
        """Updates the input_data when the state of the DataProvider changes"""

        self.input_data = self.data_sink.get_data()

    # Abstract methods
    async def main(self):
        raise NotImplementedError