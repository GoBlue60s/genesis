#Bad script

# Load a configuration first to enable plane settings
Configuration file="C:/PythonProjects/genesis/data/Elections/1976/Post_1976_conf.txt"
Status

# Test 1: Settings - plane
# Change from default (dim 0, dim 1) to explicit different plane
Settings - plane horizontal="Social" vertical="Social"
Status
Undo
Status
Redo
Status