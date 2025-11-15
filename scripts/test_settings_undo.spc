# Test script for settings capture/restore with whole-object approach
# Tests all 7 Settings commands with undo/redo
# Modified to ensure actual changes are made (not setting to current values)

# Load a configuration first to enable plane settings
Configuration file="C:/PythonProjects/genesis/data/Elections/1976/Post_1976_conf.txt"
Status

# Test 1: Settings - plane
# Change from default (dim 0, dim 1) to explicit different plane
Settings - plane horizontal="Social" vertical="Left-Right"
Status
Undo
Status
Redo
Status

# Test 2: Settings - presentation layer
# Default is Matplotlib, change to PyQtGraph
Settings - presentation layer layer="PyQtGraph"
Status
Undo
Status
Redo
Status

# Test 3: Settings - plot settings
# Defaults are all False, change to True
Settings - plot settings bisector=True connector=True reference_points=True just_reference_points=False
Status
Undo
Status
Redo
Status

# Test 4: Settings - display sizing
# Defaults: axis_extra=0.1, displacement=0.04, point_size=3
# Change to significantly different values
Settings - display sizing axis_extra=0.5 displacement=0.15 point_size=8
Status
Undo
Status
Redo
Status

# Test 5: Settings - layout options
# Default: max_cols=10
# Change to different value
Settings - layout options max_cols=15 width=12 decimals=4
Status
Undo
Status
Redo
Status

# Test 6: Settings - segment sizing
# Defaults: battleground_size=0.25 (25%), core_tolerance=0.2 (20%)
# Change to significantly different values
Settings - segment sizing battleground=40 core=35
Status
Undo
Status
Redo
Status

# Test 7: Settings - vector sizing
# Defaults: vector_head_width=0.05, vector_width=0.01
# Change to significantly different values
Settings - vector sizing vector_head_width=0.15 vector_width=0.05
Status
Undo
Status
Redo
Status

# Test 8: Multiple settings changes with undo/redo
# This tests that multiple operations can be undone/redone in sequence
Settings - plane horizontal="Social" vertical="Left-Right"
Status
Settings - presentation layer layer="PyQtGraph"
Status
Settings - plot settings bisector=True connector=True reference_points=True just_reference_points=False
Status
Undo
Status
Undo
Status
Undo
Status
Redo
Status
Redo
Status
Redo
Status
