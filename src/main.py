import time
import logging
import logging.config
import yaml
import argparse

from plugin_handler import PluginHandler

"""Simple Event Loop"""

def init_argparse(logger) -> None:
    """Fetch the command line arguments and operate on them"""

    parser = argparse.ArgumentParser(description='Event Loop')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='set the logging level to logging.DEBUG')
    args = parser.parse_args()
    if args.debug:
        # override the logger configuration and set it to DEBUG in memory
        # this necessary to ensure that child loggers inherit the same setting
        with open('log_config.yml', 'r') as f:
            log_cfg = yaml.safe_load(f.read())
            log_cfg['root']['level'] = 'DEBUG'
        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger(__name__)
        logger.debug('DEBUG MODE ENABLED')

def plugin_life_info(logger, plugin_handler) -> None:
    """Displays the current responsiveness status of each loaded plugin"""
    
    whois_alive = plugin_handler.whois_alive()
    logger.info('Responsiveness of each plugin:')
    for plugin,state in whois_alive.items():
        if state is True:
            logger.info('->\t{} is Running'.format(plugin.name))
        else:
            logger.info('->\t{} is not Running'.format(plugin.name))

def main():
    """Main function that runs the application"""

    # initialize logger
    with open('log_config.yml', 'r') as f:
        log_cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger(__name__)

    # parse arguments
    init_argparse(logger)

    logger.info('Initializing event loop')
    plugin_handler = PluginHandler('plugins')
    while True:
        logger.debug('Loaded plugins: {}'.format(plugin_handler.plugins))
        plugin_handler.invoke_callback('loop', 'A simple string to manipulate')
        plugin_life_info(logger, plugin_handler)
        time.sleep(3)
        plugin_handler.update()

if __name__ == '__main__':
    main()