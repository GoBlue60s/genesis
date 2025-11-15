# Test script for Model Menu passive commands
# Tests that all passive commands work in script mode with the new 3B pattern

# Load test data
Configuration file="data/Elections/2004/ANES_2004_conf_new.txt"
Similarities file="data/Elections/2004/ANES_2004_los.txt" value_type="dissimilarities"

# Run MDS to generate an active configuration
MDS method="Torgerson" n_components=2 use_metric=False

# Test Directions command
Directions

# Test Vectors command
Vectors

# Test Status to show final state
Status
