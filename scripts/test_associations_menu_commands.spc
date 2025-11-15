# Test script for Associations Menu passive commands
# Tests that all passive commands work in script mode with the new 3B pattern

# Load test data
Configuration file="data/Elections/2004/ANES_2004_conf_new.txt"
Similarities file="data/Elections/2004/ANES_2004_los.txt" value_type="dissimilarities"

# Run MDS to generate an active configuration
MDS method="Torgerson" n_components=2 use_metric=False

# Test Distances command
Distances

# Test Ranks differences command
Ranks differences

# Test Ranks distances command
Ranks distances

# Test Ranks similarities command
Ranks similarities

# Test Scree command (requires use_metric parameter)
Scree use_metric=False

# Test Shepard command (requires axis parameter)
Shepard axis="X-axis (horizontal)"

# Test Status to show final state
Status
