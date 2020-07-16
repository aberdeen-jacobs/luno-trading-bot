from plugin import Plugin
import inspect
import os
import pkgutil
import logging

logger = logging.getLogger(__name__)

class PluginHandler(object):
    """Container for all plugins stored in a dedicated plugin folder"""
    
    def __init__(self, plugin_folder):
        """Locates the plugin folder and loads them"""
        logger.info('Initialized PluginHandler')
        self.plugin_folder = plugin_folder
        self.plugins = []
        self.seen_paths = []
        self.update()

    def update(self):
        """Detect plugins that are stored in the dedicated plugin folder"""

        self.tmp_found_plugins = []
        self.traverse_plugins(self.plugin_folder)

        # unload plugins that are no longer in the plugin directory
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
            del(plugin)

        del(self.tmp_found_plugins)
        self.seen_paths = []

    def invoke_callback(self, function, *args, plugin_list=[]):
        """Invoke a specified callback function with supplied arguments in specified plugins"""

        if plugin_list == []:
            plugin_list = self.plugins

        for plugin in plugin_list:
            callback = getattr(plugin, function)
            value = callback(*args)
            logger.debug('executing: {}.{}({})'.format(plugin.name, function, *args))
            logger.debug('return value: {}'.format(value))

    def traverse_plugins(self, package):
        """Traverse the plugin folder to retrieve all plugins"""

        imported_package = __import__(package, fromlist=[''])

        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=[''])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)

                # Load plugin into the plugins list
                for (_, c) in clsmembers:
                    # Create boolean list comparing the uniqueness of each plugin against the new plugin
                    is_not_duplicate = [c.__module__ != plugin.name for plugin in self.plugins]

                    # Only add classes that are a non duplicate sub class of Plugin, but NOT Plugin itself
                    if issubclass(c, Plugin) & (c is not Plugin) & all(is_not_duplicate):
                        logger.info('Loaded plugin class: {}.{}'.format(c.__module__, c.__name__))
                        self.plugins.append(c())

                # Append modules from child directory
                self.tmp_found_plugins += [c().name for (_, c) in clsmembers]

        # Now that we have looked at all the modules in the current package, start looking
        # recursively for additional modules in sub packages
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
