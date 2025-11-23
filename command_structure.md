# Command Structure 
- For each command there is a class, within the class execute determines what will happen.  Execute should not contain any if statements or try/- - except blocks. It should never raise an exception. A command consists of - the following in exactly this order.

## 1. Initialize variables  this sets the variables needed to do the work of the command.
1. required
2. sets a  local path to the outside variables by setting _director equal -  to director.
3. sets the name of the command.  
4. deprecated - sets the title for the output using string or lambda expression with  - variables
Needs to be checked against command's entry in title_generator_dict - report and discrepancy
5. sets the description of errors
6. __init__

## 2. Deprecated statements
1. optional
2. If any of the calls on record_command_as_selected_and_in_process(), optionally_explain_what_command_does(), and detect_dependency_problem() appear, they should all be removed

## 3. Record command as initiated
1. required
2. initiate_command_processes()

## 4. Display plot to supply information user needs to set setting
1. extremely rare - only Alike command
2. should not be shown if mode is script
3. create_plot_for_tabs("cutoff")

## 5. Get any needed settings from user
1. optional
2. get_command_parameters

## 6. Capture state for undo
1. required - except for Open script
2. capture_and_push_undo_state

## 7. Read file
1. conditional
2. read file

## 8. Check for consistency with existing features
1. conditional - only use when command, other than open script,
 has a read file or creates a feature
2. detect_consistency_issues

## 9. Perform the requested action inherent in the command
1. optional
2. such as  inter_point_distances, rank_when_similarities_match_X, Rivalry

## 10. Print on Record tab
1. required - except for Open script, Shepard
2. print_X

## 11. Create plot
1. conditional 
2. create_plot_for_tabs(“X”)

## 12. Create title for table widget depending on how __init__ sets title
1. deprecated - This should not be present in execute.
2. title_generator_dict must have key for this command and value should be
based on what had been in __init__ or what was in execute

## 13. Create_table_for_<command>
1. required
2. create_widgets_for_output_and_log_tabs

## 14. if no plot
1. conditional - only needed if there is no plot, if there is a plot no line is needed as that would be redundant
2. set_focus_on_tab(“Output”)

## 15. end of command
1. required
2. record_command_as_successfully_completed

