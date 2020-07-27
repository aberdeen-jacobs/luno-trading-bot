import signal
import asyncio
import time
import logging
import logging.config
import yaml
import argparse
from event_loop import EventLoop

"""Driver module"""

logger = logging.getLogger(__name__)

def init_argparse() -> None:
    """Fetch the command line arguments and operate on them"""

    global logger
    parser = argparse.ArgumentParser(description='Event Loop')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='set the logging level to logging.DEBUG')
    args = parser.parse_args()
    if args.debug:
        # Override the logger configuration and set it to DEBUG in memory
        # This necessary to ensure that child loggers inherit the same setting
        with open('log_config.yml', 'r') as f:
            log_cfg = yaml.safe_load(f.read())
            log_cfg['root']['level'] = 'DEBUG'
        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger(__name__)
        logger.debug('DEBUG MODE ENABLED')

def plugin_heartbeat(logger, plugin_handler) -> None:
    """Displays the current responsiveness status of each loaded plugin"""

    whois_alive = plugin_handler.whois_alive()
    logger.info('Responsiveness of each plugin:')
    for plugin,state in whois_alive.items():
        if state:
            logger.info('->\t{} is Running'.format(plugin.name))
        else:
            logger.info('->\t{} is not Running'.format(plugin.name))

async def exit():
    """Stopping the asyncio event loop"""

    loop = asyncio.get_event_loop()
    logger.debug('Safely stopping the asyncio event loop')
    loop.stop()

def clean_exit():
    """Cleaning up the asyncio tasks"""

    for task in asyncio.all_tasks():
        logger.debug('Cancelling the {} task in asyncio'.format(task))
        task.cancel()
    asyncio.ensure_future(exit())

def main():
    """Main function that runs the application"""

    # Initialize logger
    with open('log_config.yml', 'r') as f:
        global logger
        log_cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger(__name__)

    # Parse arguments
    init_argparse()

    logger.info('Initializing the event loop')
    event_loop = EventLoop()
    loop = asyncio.get_event_loop()

    # Run the asyncio event loop
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:          
        loop.add_signal_handler(sig, clean_exit)
    try:
        asyncio.ensure_future(event_loop.data_provider_loop())
        asyncio.ensure_future(event_loop.plugins_runner())
        loop.run_forever()
    finally:
        logging.info('Shutting down event loop')
        loop.close()


if __name__ == '__main__':
    main()