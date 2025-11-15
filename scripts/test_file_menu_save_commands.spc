# Test script for file menu Save commands
# Tests that all Save commands work in script mode with the new 3B pattern

# Load configuration and test Save configuration
Configuration file="data/Elections/2004/ANES_2004_conf_new.txt"
Save configuration file="data/test_save_config.txt"

# Load similarities and test Save similarities
Similarities file="data/Elections/2004/ANES_2004_los.txt" value_type="dissimilarities"
Save similarities file="data/test_save_similarities.txt"

# Note: The following Save commands require specific data types to be loaded first
# Uncomment and test as needed when the corresponding data is available

# Save correlations (requires correlations data)
# Correlations file="data/Elections/2004/correlations.txt"
# Save correlations file="data/test_save_correlations.csv"

# Save grouped data (requires grouped data)
# Grouped data file="data/Elections/2004/grouped_data.txt"
# Save grouped data file="data/test_save_grouped.txt"

# Save individuals (requires individuals data)
# Individuals file="data/Elections/2004/individuals.csv"
# Save individuals file="data/test_save_individuals.csv"

# Save sample design (requires uncertainty/sample design)
# Save sample design file="data/test_save_sample_design.txt"

# Save sample repetitions (requires uncertainty/sample repetitions)
# Save sample repetitions file="data/test_save_sample_reps.txt"

# Save sample solutions (requires uncertainty/sample solutions)
# Save sample solutions file="data/test_save_sample_solutions.txt"

# Save scores (requires scores data)
# Scores file="data/Elections/2004/scores.csv"
# Save scores file="data/test_save_scores.csv"

# Save target (requires target configuration)
# Target file="data/Elections/2004/target.txt"
# Save target file="data/test_save_target.txt"

# Show final status
Status
