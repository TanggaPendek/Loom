import importlib.util
import os
import sys


class ModuleLoader:
    def __init__(self, base_path=None):
        """
        Handles dynamic loading of Python modules from Loom/codebank.
        """
        if base_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.join(current_dir, "..", "..", "nodebank")
            base_path = os.path.normpath(base_path)

        self.base_path = base_path

        if self.base_path not in sys.path:
            sys.path.append(self.base_path)

    def load_module(self, module_path):
        """
        Loads a Python file as a full module.
        Example:
            loader.load_module("standard/test_module.py")
        """
        abs_path = os.path.join(self.base_path, module_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Module not found: {abs_path}")

        # Load dynamically
        spec = importlib.util.spec_from_file_location("dynamic_module", abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
