# Test script for file menu Print and Save commands
# Tests that the commands work in script mode with the new 3B pattern

# Load test data
Configuration file="data/Elections/2004/ANES_2004_conf_new.txt"

# Test Print configuration command
Print configuration

# Test Save configuration command
Save configuration file="data/test_config_output.txt"

# Load similarities and test Print/Save
Similarities file="data/Elections/2004/ANES_2004_los.txt" value_type="dissimilarities"
Print similarities
Save similarities file="data/test_similarities_output.txt"

# Test other Print commands (commented out - require specific data)
# Correlations file="data/Elections/2004/2004_correlations.txt"
# Print correlations
# Save correlations file="data/test_correlations_output.csv"

# Evaluations file="data/Elections/2004/2004_evaluations.txt"
# Print evaluations

# Grouped data file="data/Elections/2004/2004_grouped.txt"
# Print grouped data
# Save grouped data file="data/test_grouped_output.txt"

# Individuals file="data/Elections/2004/2004_individuals.txt"
# Print individuals
# Save individuals file="data/test_individuals_output.csv"

# Scores file="data/Elections/2004/2004_scores.txt"
# Print scores
# Save scores file="data/test_scores_output.csv"

# Target file="data/Elections/2004/2004_target.txt"
# Print target
# Save target file="data/test_target_output.txt"

# Test Status to show final state
Status
