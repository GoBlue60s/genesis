# Test script for file menu Print commands
# Tests that the commands work in script mode with the new 3B pattern
# These commands require active data to be loaded first

# Load some test data first
Configuration "data/Elections/2004/2004.txt"

# Test Print configuration command
Print configuration

# Test Print correlations command (needs correlations loaded)
# Correlations "data/Elections/2004/2004_correlations.txt"
# Print correlations

# Test Print evaluations command (needs evaluations loaded)
# Evaluations "data/Elections/2004/2004_evaluations.txt"
# Print evaluations

# Test Print grouped data command (needs grouped data loaded)
# Grouped data "data/Elections/2004/2004_grouped.txt"
# Print grouped data

# Test Print individuals command (needs individuals loaded)
# Individuals "data/Elections/2004/2004_individuals.txt"
# Print individuals

# Test Print sample design command (needs uncertainty run)
# Print sample design

# Test Print sample repetitions command (needs uncertainty run)
# Print sample repetitions

# Test Print sample solutions command (needs uncertainty run)
# Print sample solutions

# Test Print scores command (needs scores loaded)
# Scores "data/Elections/2004/2004_scores.txt"
# Print scores

# Test Print similarities command (needs similarities loaded)
Similarities "data/Elections/2004/2004.txt"
Print similarities

# Test Print target command (needs target loaded)
# Target "data/Elections/2004/2004_target.txt"
# Print target

# Test Status to show the final state
Status
