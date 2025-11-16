# Command Structure 
- For each command there is a class, within the class execute determines  - what will happen.  execute should not contain any if statements or try/- - except blocks. It should never raise an exception. A command consists of - the following in exactly this order.

## 1. Initialize variables  this sets the variables needed to do the work of the command.
1. required
2. sets a  local path to the outside variables by setting _director equal -  to director.
3. sets the name of the command.  
4. deprecated - sets the title for the output using string or lambda expression with  - variables
5. sets the description of errors
6. __init__

## 2. Record command as selected
1. required
2. record_command_as_selected_and_in_process

## 3. If verbose is true add explanation to output
1. required
1. optionally_explain_what_command_does

## 4. Check whether dependencies are satisfied
1. required
2. detect_dependency_problems

## 5. Get any needed settings from user
1. optional
2. get_command_parameters

## 6. Capture state for undo
1. required
2. capture_and_push_undo_state

## 7. Read file
1. conditional
2. read file

## 8. Check for consistency with existing features
1. conditional
2. detect_consistency_issues

## 9. Perform the requested action inherent in the command
1. optional
2. such as  inter_point_distances, rank_when_similarities_match_X, Rivalry

## 10. Print
1. required
2. print_X

## 11. Create plot
1. conditional 
2. create_plot_for_tabs(“X”)

## 12. Create title for table widget depending on how __init__ sets title
1. deprecated
2.title_for_table_widget = title_generator() or  = table_for_title

## 13. Create_table_for_<command>
1. required
2. create_widgets_for_output_and_log_tabs

## 14. if no plot
1. conditional
1. set_focus_on_tab(“Output”)

## 15. end of command
1. required
2. record_command_as_successfully_completed

