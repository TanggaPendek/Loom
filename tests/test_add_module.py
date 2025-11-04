import unittest
from executor.utils.module_loader import ModuleLoader

class TestAddModule(unittest.TestCase):
    def setUp(self):
        self.loader = ModuleLoader()
        self.mod = self.loader.load_module("standard/add.py")

    def test_add_default(self):
        # Check that the function works with its default input
        self.assertEqual(self.mod.add([1, 9, 90]), 100)

    def test_add_override_input(self):
        # Override the module variable and test again
        self.mod.input = [10, 20, 30]
        result = self.mod.add(self.mod.input)
        self.assertEqual(result, 60)

if __name__ == "__main__":
    unittest.main()
