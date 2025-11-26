# Spaces Script - Test Rivalry Undo/Redo
# This script tests the capture/restore cycle for rivalry
# Created: 2025-11-11

# Step 1: Load configuration file
Configuration file="C:/PythonProjects/genesis/data/Elections/1976/Post_1976_conf.txt"

# Step 2: Set first pair of reference points (Carter vs Ford)
Reference points contest=['Carter', 'Ford']

# Step 3: Set second pair of reference points (Reagan vs Mondale) - should capture state before replacing
Reference points contest=['Reagan', 'Mondale']

# Step 4: Test undo - should restore to first reference points (Carter vs Ford)
Undo

# Step 5: Test redo - should restore to second reference points (Reagan vs Mondale)
Redo
