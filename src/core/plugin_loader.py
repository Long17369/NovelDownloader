import os
import sys

import importlib.util
from types import ModuleType

from .base import BasePlugin, plugin_list

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "src/plugins")


class PluginLoader:
    def __init__(self, plugin_dir: str = PLUGIN_DIR):
        self.plugin_dir = plugin_dir
        self.plugins: dict[str, ModuleType] = self.load_plugins()
        self.plugin_list = self.handle_plugin()

    def handle_plugin(self):
        res: list[tuple[int, BasePlugin]] = []
        for plugin in plugin_list:
            res.append((plugin.priority, plugin()))
        res.sort(key=lambda x: x[0], reverse=True)
        return res

    def load_plugins(self):
        plugins: dict[str, ModuleType] = {}
        if not os.path.isdir(PLUGIN_DIR):
            return plugins

        sys.path.insert(0, PLUGIN_DIR)
        for filename in os.listdir(PLUGIN_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(PLUGIN_DIR, filename)
                    )
                    if spec is None or spec.loader is None:
                        print(
                            f"Failed to load plugin {module_name}: spec or loader is None"
                        )
                        continue
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    plugins[module_name] = module
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")
        sys.path.pop(0)
        return plugins

    def reload_plugins(self):
        """
        reload_plugins 的 Docstring

        :param self: 说明
        还未实现
        """
        plugin_list.clear()
        self.plugins = self.load_plugins()
        self.plugin_list = self.handle_plugin()


# Example usage:
# plugins = load_plugins()
# print(plugins)
