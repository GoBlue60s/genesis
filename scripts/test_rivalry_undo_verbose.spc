# Spaces Script - Comprehensive Rivalry Undo/Redo Test
# This script thoroughly tests the capture/restore cycle for rivalry
# Created: 2025-11-11

# Set verbose mode to see detailed output
Verbose

# Step 1: Load configuration file
Configuration file="C:/PythonProjects/genesis/data/Elections/1976/Post_1976_conf.txt"

# Step 2: Set first pair of reference points (Carter vs Ford)
Reference points contest=['Cart', 'Ford']

# Step 3: Show status and configuration to see rivalry details
Status
View configuration

# Step 4: Set second pair of reference points (Reagan vs Mondale)
Reference points contest=['Reag', 'Mond']

# Step 5: Show status and configuration to see changed rivalry details
Status
View configuration

# Step 6: Undo - should restore to first reference points (Carter vs Ford)
Undo

# Step 7: Show status and configuration to verify restoration
Status
View configuration

# Step 8: Redo - should restore to second reference points (Reagan vs Mondale)
Redo

# Step 9: Show final status and configuration to verify restoration
Status
View configuration
