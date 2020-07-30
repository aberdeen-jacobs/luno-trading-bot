import time
import asyncio
import logging
from observer import Observer, Observable

logger = logging.getLogger(__name__)

class DataProvider(Observable):
    """[summary]
    """

    def __init__(self):
        super().__init__()
        self.data = None

    def set_data(self, data: dict):
        """Primitive data setter method

        :param data: Dict object which observers require
        :type data: dict
        """

        self.data = data

    def get_data(self) -> dict:
        """Data getter method

        :return: Dict object that was stored for transmission
        :rtype: dict
        """
        
        return self.data
    
    async def broadcast(self, data: dict):
        """Broadcast data to the observers by updating state of the provider
        and the subsequently notifying all observers

        :param data: The data that will be broadcasted to all subscribed observers
        :type data: str
        """

        self.set_data(data)
        self.set_changed()
        await self.notify_observers()