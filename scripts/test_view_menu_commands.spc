# Test script for View Menu passive commands
# Tests that all View commands work in script mode with the new 3B pattern

# Load test data
Configuration file="data/Elections/2004/ANES_2004_conf_new.txt"
Similarities file="data/Elections/2004/ANES_2004_los.txt" value_type="dissimilarities"

# Test History command
History

# Test View configuration command
View configuration

# Test View correlations command (commented out - requires correlations data)
# Correlations file="data/Elections/2004/correlations.txt"
# View correlations

# Test View custom command
View custom

# Test View distances command
View distances

# Test View evaluations command (commented out - requires evaluations data)
# Evaluations file="data/Elections/2004/evaluations.txt"
# View evaluations

# Test View grouped data command (commented out - requires grouped data)
# Grouped data file="data/Elections/2004/grouped_data.txt"
# View grouped data

# Test View individuals command (commented out - requires individuals data)
# Individuals file="data/Elections/2004/individuals.csv"
# View individuals

# Test View sample design command (commented out - requires uncertainty/sample design)
# View sample design

# Test View sample repetitions command (commented out - requires uncertainty/sample repetitions)
# View sample repetitions

# Test View sample solutions command (commented out - requires uncertainty/sample solutions)
# View sample solutions

# Test View scores command (commented out - requires scores data)
# Scores file="data/Elections/2004/scores.csv"
# View scores

# Test View similarities command
View similarities

# Test View spatial uncertainty command (commented out - requires uncertainty data and plot parameter)
# View spatial uncertainty plot="mean"

# Test View target command (commented out - requires target configuration)
# Target file="data/Elections/2004/target.txt"
# View target

# Test Status to show final state
Status
