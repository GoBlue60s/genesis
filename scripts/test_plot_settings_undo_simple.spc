# Simple test for Settings - plot settings undo/redo
# Load a configuration first
Configuration file="C:/PythonProjects/genesis/data/Elections/1976/Post_1976_conf.txt"
Status

# Change plot settings from defaults (all False) to True
Settings - plot settings bisector=True connector=True reference_points=True just_reference_points=False
Status

# Undo - should show the plot settings that were restored
Undo
Status

# Redo - should show the plot settings that were restored
Redo
Status
