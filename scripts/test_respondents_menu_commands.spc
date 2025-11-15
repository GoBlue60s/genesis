# Test script for Respondents Menu passive commands
# Tests that all passive commands work in script mode with the new 3B pattern

# Load respondent scores and configuration
Open scores file="data/Elections/2004/ANES_2004_scores_inverted.csv"
Configuration file="data/Elections/2004/ANES_2004_conf_inverted.txt"

# Test Joint command (shows reference points and individuals)
Joint

# Set up rivalry for Contest and Segments commands
Reference points contest=['gwbush', 'kerry']

# Test Contest command (shows regions defined by reference points)
Contest

# Test Segments command (shows regions defined by individual scores)
Segments

# Test Status to show final state
Status
