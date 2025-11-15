# Spaces Script - Test Grouped Data Undo/Redo
# This script tests the capture/restore cycle for grouped_data
# Created: 2025-11-11

# Step 1: Load first grouped data file
Grouped data file="C:/PythonProjects/genesis/data/Elections/1976/Gender_1976.txt"

# Step 2: Load second grouped data file (should capture state before replacing)
Grouped data file="C:/PythonProjects/genesis/data/Elections/1976/Gender_1976.txt"

# Step 3: Test undo - should restore to first grouped data
Undo

# Step 4: Test redo - should restore to second grouped data
Redo
