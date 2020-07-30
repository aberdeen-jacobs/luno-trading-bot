import inspect
import os
import pkgutil
import asyncio
import logging
from plugin import Plugin
from data_provider import DataProvider

logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()

class PluginHandler(object):
    """Container for all plugins stored in a dedicated plugin folder"""

    def __init__(self, plugin_folder: str, data_sink: DataProvider):
        """Locates the plugin folder and loads them"""

        logger.info('Initialized PluginHandler')
        self.plugin_folder = plugin_folder
        self.data_sink = data_sink
        self.seen_paths = []
        self.plugins = []
        self.enabled_plugins = []
        self.completed_task = {}
        self.update()

    def update(self) -> None:
        """Detect plugins that are stored in the dedicated plugin folder"""

        self.tmp_found_plugins = []
        self.traverse_plugins(self.plugin_folder)

        # Unload plugins that are no longer in the plugin directory
        tmp_loaded_plugins = [plugin.name for plugin in self.plugins]
        obsolete_plugin_names = list(set(tmp_loaded_plugins) - set(self.tmp_found_plugins))
        obsolete_plugins = []
        for plugin_name in obsolete_plugin_names:
            for plugin in self.plugins:
                if plugin_name == plugin.name:
                    obsolete_plugins.append(plugin)

        for plugin in obsolete_plugins:
            logger.info('Unloaded plugin class: {}.{}'.format(plugin.name, plugin.__class__.__name__))
            self.plugins.remove(plugin)
            # Remove plugin from enabled plugins list and unsubscribe from observable
            if plugin in self.enabled_plugins:
                self.enabled_plugins.remove(plugin)
                self.data_sink.delete_observer(plugin)
            del(plugin)

        del(self.tmp_found_plugins)
        self.seen_paths = []

    async def invoke_callback(self, *instr, plugin_list=[None]):
        """Invoke a specified callback function with supplied arguments in specified plugins

        :return: A dictionary consisting of pairs of plugins and their returned objects
        :rtype: dict
        """

        function = instr[0]
        args = instr[1:]

        if plugin_list == [None]:
            plugin_list = self.enabled_plugins

        for plugin in plugin_list:
            # Check if previously run task is done before creating new task
            if self.completed_task[plugin].done():
                callback = getattr(plugin, function)
                task = asyncio.ensure_future(callback(*args))
                self.completed_task[plugin] = task
                logger.debug('Executing function: {}.{}, with arguments: {}'.format(plugin.name, function, args))

    async def whois_alive(self) -> dict:
        """Invoke the heartbeat callback on each loaded plugin

        :return: A dictionary of plugins paired with their responsiveness state
        :rtype: dict
        """

        completed_tasks = await self.invoke_callback('heartbeat')
        is_alive_dict = { plugin:(True if plugin in completed_tasks else False) for plugin in self.plugins }
        return is_alive_dict

    def traverse_plugins(self, package) -> None:
        """Traverse the plugin folder to retrieve all plugins"""

        imported_package = __import__(package, fromlist=[''])

        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=[''])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)

                # Load plugin into the plugins list
                for (_, c) in clsmembers:
                    if issubclass(c, Plugin):
                        plugin_obj = c(self.data_sink)
                    else:
                        plugin_obj = c()

                    # Create boolean list comparing the uniqueness of each plugin against the new plugin
                    is_not_duplicate = [c.__module__ != plugin.name for plugin in self.plugins]

                    # Only add classes that are a non duplicate sub class of Plugin, but NOT Plugin itself
                    if issubclass(c, Plugin) & (c is not Plugin) & all(is_not_duplicate):
                        logger.info('Loaded plugin class: {}.{}'.format(c.__module__, c.__name__))
                        # Add plugin to list of plugins, enabled plugins and subscribe to observable
                        self.plugins.append(plugin_obj)
                        self.enabled_plugins.append(plugin_obj)
                        self.completed_task[plugin_obj] = asyncio.ensure_future(asyncio.sleep(0.01))
                        self.data_sink.add_observer(plugin_obj)

                    # Append modules from child directory
                    if issubclass(c, Plugin):
                        self.tmp_found_plugins.append(plugin_obj.name)

        # Look recursively for additional modules in sub packages
        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])
        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                # Get all sub directory of the current package path directory
                child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]

                # For each sub directory, apply the walk_package method recursively
                for child_pkg in child_pkgs:
                    self.traverse_plugins(package + '.' + child_pkg)

    def get_plugin_obj(self, plugin_name: str) -> Plugin:
        """Match the plugin object given the plugin name

        :param plugin_name: Name of the plugin, for example 'plugins.name'
        :type input: str
        :return: Plugin object
        :rtype: Plugin
        """

        # O(n) is reasonable if number of plugins are few
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None

    def is_enabled(self, plugin: Plugin) -> bool:
        """Indicate whether plugin is enabled or not

        :param plugin: Plugin which is loaded
        :type plugin: Plugin
        :return: If enabled then True, otherwise False
        :rtype: bool
        """

        return True if plugin in self.enabled_plugins else False

    def disable(self, plugin: Plugin) -> bool:
        """Disable plugin by removing it from the enabled plugins list and
        unsubscribing from the observable

        :param plugin: Plugin to be disabled
        :type plugin: Plugin
        :return: If successfully disabled then True, otherwise False
        :rtype: bool
        """
        if plugin in self.enabled_plugins:
            self.enabled_plugins.remove(plugin)
            self.data_sink.delete_observer(plugin)
            logger.info('Disabled plugin {}'.format(plugin.name))
            return True
        return False

    def enable(self, plugin: Plugin) -> bool:
        """Enable plugin by adding it to the enabled plugins list and
        subscribing to the observable

        :param plugin: Plugin to be enabled
        :type plugin: Plugin
        :return: If successfully enabled then True, otherwise False
        :rtype: bool
        """
        
        if plugin in self.plugins:
            self.enabled_plugins.append(plugin)
            self.data_sink.add_observer(plugin)
            logger.info('Enabled plugin {}'.format(plugin.name))
            return True
        return False