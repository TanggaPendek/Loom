from module_loader import ModuleLoader

loader = ModuleLoader()  # automatically finds Loom/codebank
add_func = loader.load_module("standard/add.py")
add_func.input = [20,1000,10]
new = add_func.add(add_func.input)
print(new)