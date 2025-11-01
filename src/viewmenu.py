from __future__ import annotations

# import numpy as np
import pandas as pd
import peek
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
	QDialog,
	QTableWidget,
	QTableWidgetItem,
	QTextEdit,
)

# Local application imports

from common import Spaces
from exceptions import SpacesError
from dialogs import ModifyItemsDialog

if TYPE_CHECKING:
	from director import Status

# ------------------------------------------------------------------------


class HistoryCommand:
	"""The History command displays the commands used in
	this session.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		director.command = "History"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._print_history()
		self._director.title_for_table_widget = "Commands used"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

		# --------------------------------------------------------------------

	def _print_history(self) -> None:
		commands_used = self._director.commands_used
		command_exit_code = self._director.command_exit_code

		print("\n\tCommands used\n")

		# Create header
		header = f"\t{'Command':<40} {'Status':<25}"
		print(header)
		print("\t" + "-" * 65)

		# Print each command with proper alignment
		range_commands_used = range(1, len(commands_used))
		for i in range_commands_used:
			command = commands_used[i]
			status = command_exit_code[i]
			match status:
				case 1:
					status_str = "Failed"
				case 0:
					status_str = "Completed successfully"
				case -1:
					status_str = "In process"
				case _:
					status_str = "Unknown status"

			line = f"\t{command:<40} {status_str:<25}"
			print(line)
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_history()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget, ["Command", "Status"], []
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_history_initialize_variables(self) -> None:
		self.unknown_status_of_command_error_title = "History"
		self.unknown_status_of_command_error_message = (
			"Commands used has unknown value"
		)

	# ------------------------------------------------------------------------

	def _create_table_widget_for_history(self) -> QTableWidget:
		self._create_table_widget_for_history_initialize_variables()
		commands_used = self._director.commands_used
		command_exit_code = self._director.command_exit_code

		table_widget = QTableWidget(len(commands_used), 2)
		#
		range_commands_used = range(1, len(commands_used))
		for each_command in range_commands_used:
			table_widget.setItem(
				each_command, 0, QTableWidgetItem(commands_used[each_command])
			)
			status = command_exit_code[each_command]
			match status:
				case 1:
					status_str = "Failed"
				case 0:
					status_str = "Completed successfully"
				case -1:
					status_str = "In process"
				case _:
					raise SpacesError(
						self.unknown_status_of_command_error_title,
						self.unknown_status_of_command_error_message,
					)
			#
			table_widget.setItem(each_command, 1, QTableWidgetItem(status_str))
		return table_widget

	# ------------------------------------------------------------------------


class ViewConfigurationCommand:
	"""The View configuration command displays the active configuration ."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View configuration"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_configuration()
		self._director.common.create_plot_for_tabs("configuration")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewCorrelationsCommand:
	"""The View correlations command presents correlations
	among evaluations. These can be used as similarities
	for multidimensional scaling
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View correlations"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# common.print_lower_triangle(self._director.correlations_active)
		self._director.correlations_active.print_the_correlations(
			self._director.common.width, self._director.common.decimals, common
		)
		# self._director.correlations_active)
		self._director.common.create_plot_for_tabs("heatmap_corr")
		nreferent = self._director.correlations_active.nreferent
		self._director.title_for_table_widget = (
			f"Correlation matrix has {nreferent} items"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewCustomCommand:
	"""The View custom command displays the active configuration
	using custom ranges on the dimensions.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View custom"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._print_view_custom()
		self._create_view_custom_plot_for_tabs_using_matplotlib()
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_view_custom(self) -> None:
		npoint = self._director.configuration_active.npoint
		ndim = self._director.configuration_active.ndim

		print(
			"\n\tConfiguration has", ndim, "dimensions and", npoint, "points\n"
		)
		self._director.configuration_active.print_active_function()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget | QTextEdit:
		#

		dim_names = self._director.configuration_active.dim_names
		point_names = self._director.configuration_active.point_names
		point_coords = self._director.configuration_active.point_coords

		gui_output_as_widget = self._create_table_widget_from_config(
			point_coords
		)
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget, dim_names, point_names
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	@staticmethod
	def _create_table_widget_from_config(config: pd.DataFrame) -> QTableWidget:
		#
		n_rows = config.shape[0]
		n_cols = config.shape[1]
		#
		table_widget = QTableWidget(n_rows, n_cols)
		#
		for each_point in range(n_rows):
			for each_dim in range(n_cols):
				value = f"{config.iloc[each_point, each_dim]:8.4f}"
				table_widget.setItem(
					each_point, each_dim, QTableWidgetItem(value)
				)
		return table_widget

	# ------------------------------------------------------------------------


class ViewDistancesCommand:
	"""View distances command - displays a matrix of inter-point distances."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View distances"
		self._width = 8
		self._decimals = 2
		self._director.configuration_active.nreferent = (
			self._director.configuration_active.npoint
		)
		self._director.title_for_table_widget = "Inter-point distances"
		return

		# --------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_distances(
			self._width, self._decimals, common
		)
		self._director.common.create_plot_for_tabs("heatmap_dist")
		self._director.title_for_table_widget = "Inter-point distances"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewEvaluationsCommand:
	"""The View evaluations command displays the active evaluations."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View evaluations"
		self._director.width = 8
		self._director.decimals = 2

		return

		# --------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("evaluations")
		self._director.title_for_table_widget = "Evaluations"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewGroupedDataCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		director.command = "View grouped data"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		ndim = self._director.grouped_data_candidate.ndim
		ngroups = self._director.grouped_data_candidate.ngroups

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.grouped_data_active.print_grouped_data()
		self._director.common.create_plot_for_tabs("grouped_data")
		grouping_var = self._director.grouped_data_active.grouping_var
		self._director.title_for_table_widget = (
			f"Configuration is based on {grouping_var}"
			f" and has {ndim} dimensions and {ngroups} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewIndividualsCommand:
	"""The View individuals command displays the active individuals."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View individuals"
		self._director.width = 8
		self._director.decimals = 2

		return

		# --------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.individuals_active.print_individuals()
		# self._director.common.create_plot_for_tabs(
		# "individuals")
		self._director.title_for_table_widget = "Individuals"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewPointUncertaintyCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Point Uncertainty Command...."""
		self._director = director
		self.common = common
		self._director.command = "View point uncertainty"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, plot: str) -> None:

		self.plot_to_show = plot

		director = self._director
		common = self.common
		uncertainty_active = director.uncertainty_active
		point_names = uncertainty_active.point_names

		# Store plot visualization mode for plotting functions
		director.plot_to_show = plot

		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()

		# Get command parameters (will use dialog if interactive)
		# Pass plot as kwarg since it comes from execute method
		params = common.get_command_parameters("View point uncertainty", plot=plot)
		selected_points: list[str] = params["points"]

		# Validate selection
		if not selected_points:
			selection_required_title = "Selection required"
			selection_required_message = (
				"At least one point must be selected"
			)
			raise SpacesError(
				selection_required_title, selection_required_message
			)

		# Convert selected point names to indices
		selected_indices = [
			point_names.index(point) for point in selected_points
		]

		# Store selected point indices for plotting functions
		director.selected_point_indices = selected_indices

		# Record command for script generation
		common.capture_and_push_undo_state(
			"View point uncertainty",
			"passive",
			params
		)

		# Create the point uncertainty plot
		common.create_plot_for_tabs("point_uncertainty")

		director.title_for_table_widget = (
			f"Point Uncertainty - "
			f"{len(selected_indices)} points: {', '.join(selected_points)}"
		)
		director.create_widgets_for_output_and_log_tabs()
		director.set_focus_on_tab("Plot")
		director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------


class ViewSampleDesignCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Sample design command is used to view a sample design."""
		self._director = director
		self.common = common
		self._director.command = "View sample design"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		sample_design = self._director.uncertainty_active.sample_design
		print(sample_design)
		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = (
			self._director.uncertainty_active.probability_of_inclusion
		)
		self._director.title_for_table_widget = (
			f"Sample design - Size of universe: {universe_size},"
			f" Probability of inclusion: "
			f"{probability_of_inclusion}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._director.uncertainty_active.\
			create_table_widget_for_sample_designer()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			[
				"Repetition",
				"Selected \n N",
				"Percent",
				"Not selected \n N",
				"Percent",
			],
			[],
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget


#  --------------------------------------------------------------------------


class ViewSampleRepetitionsCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Sample repetitions command is used to view sample
		repetitions.
		"""
		self._director = director
		self.common = common
		self._director.command = "View sample repetitions"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		print(self._director.uncertainty_active.sample_repetitions)
		self._director.title_for_table_widget = "Sample repetitions"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._director.uncertainty_active.\
			create_table_widget_for_sample_designer()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			[
				"Repetition",
				"Selected \n N",
				"Percent",
				"Not selected \n N",
				"Percent",
			],
			[],
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget


#  --------------------------------------------------------------------------


class ViewSampleSolutionsCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Sample Solutions command is used to view
		sample solutions."""
		self._director = director
		self.common = common
		self._director.command = "View sample solutions"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# print(self._director.uncertainty_active.sample_solutions)
		nsolutions = self._director.uncertainty_active.nsolutions
		ndim = self._director.uncertainty_active.ndim
		npoint = self._director.uncertainty_active.npoints
		self._director.title_for_table_widget = (
			f"{nsolutions} solutions have {ndim} dimensions "
			f"and {npoint} points"
		)
		common.create_solutions_table()
		common.print_sample_solutions()
		common.create_plot_for_tabs("uncertainty")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._director.statistics.display_table(
			"sample_solutions"
		)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------


class ViewScoresCommand:
	"""The View scores command displays the active scores."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		director.command = "View scores"
		self._width = 8
		self._decimals = 2

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		nscores = self._director.scores_active.nscores
		nscored = self._director.scores_active.nscored_individ

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.title_for_table_widget = (
			f"There are {nscores} active scores for {nscored} individuals."
		)
		self._director.common.create_plot_for_tabs("scores")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewSimilaritiesCommand:
	"""The View similarities command is used to display similarities
	between the points.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View similarities"
		self._width = 8
		self._decimals = 2
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		value_type = self._director.similarities_active.value_type
		nreferent = self._director.similarities_active.nreferent

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common
		)
		self._director.title_for_table_widget = (
			f"The {value_type} matrix has {nreferent} items"
		)
		self._director.common.create_plot_for_tabs("heatmap_simi")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewSpatialUncertaintyCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Spatial Uncertainty Command...."""
		self._director = director
		self.common = common
		self._director.command = "View spatial uncertainty"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, plot: str) -> None:
		director = self._director
		uncertainty_active = director.uncertainty_active
		sample_solutions = uncertainty_active.sample_solutions
		nsolutions = uncertainty_active.nsolutions
		ndim = uncertainty_active.ndim
		npoint = uncertainty_active.npoints

		self.plot_to_show = plot
		director.plot_to_show = plot  # Store for plotting functions
		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()

		# Record command for script generation
		self.common.push_passive_command_to_undo_stack(
			"View spatial uncertainty",
			{"plot": plot}
		)

		print(sample_solutions)

		# Create the plot with the specified visualization mode
		common.create_plot_for_tabs("spatial_uncertainty")

		director.title_for_table_widget = (
			f"Spatial Uncertainty - {nsolutions} solutions "
			f"with {ndim} dimensions and {npoint} points"
		)
		director.create_widgets_for_output_and_log_tabs()
		director.set_focus_on_tab("Plot")
		director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewTargetCommand:
	"""The View target command displays the target configuration ."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View target"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		ndim = self._director.target_active.ndim
		npoint = self._director.target_active.npoint

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.target_active.print_target()
		self._director.common.create_plot_for_tabs("target")
		self._director.title_for_table_widget = (
			f"Target configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewUncertaintyCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The View Uncertainty Command...."""
		self._director = director
		self.common = common
		self._director.command = "View uncertainty"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		nscores = self._director.scores_active.nscores
		nscored = self._director.scores_active.nscored_individ

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.common.create_plot_for_tabs("scores")
		self._director.title_for_table_widget = (
			f"There are {nscores} active scores for {nscored} individuals."
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewScriptCommand:
	"""The View script command displays the command history that can be
	saved as a script.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "View script"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._print_script()
		self._director.title_for_table_widget = "Script commands"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_script(self) -> None:
		# Get command history from undo stack (same as SaveScriptCommand)
		undo_stack = self._director.undo_stack

		print("\n\tScript commands\n")
		for cmd_state in undo_stack:
			# Skip commands with empty names
			if not cmd_state.command_name:
				continue

			# Skip script-type commands (OpenScript, SaveScript, ViewScript)
			# These are meta-commands not appearing in generated scripts
			if cmd_state.command_type == "script":
				continue

			# Build command line with parameters
			cmd_line = cmd_state.command_name
			if cmd_state.command_params:
				formatted_params = self.common.format_parameters_for_display(
					cmd_state.command_name, cmd_state.command_params
				)
				param_parts = []
				for key, value in formatted_params.items():
					if isinstance(value, str):
						# String values - always add quotes for safety
						# (names can contain spaces, making quotes necessary)
						param_parts.append(f'{key}="{value}"')
					elif isinstance(value, (list, dict)):
						# Lists and dicts - write as Python literals
						param_parts.append(f'{key}={value}')
					else:
						# Numbers, booleans, etc.
						param_parts.append(f'{key}={value}')
				params_str = " ".join(param_parts)
				cmd_line = f"{cmd_line} {params_str}"

			print(f"\t{cmd_line}")
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_script()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget, ["Command"], []
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_script(self) -> QTableWidget:
		# Get command history from undo stack (same as SaveScriptCommand)
		undo_stack = self._director.undo_stack

		# Collect commands with their parameters
		script_lines = []
		for cmd_state in undo_stack:
			# Skip commands with empty names
			if not cmd_state.command_name:
				continue

			# Skip script-type commands (OpenScript, SaveScript, ViewScript)
			# These are meta-commands not appearing in generated scripts
			if cmd_state.command_type == "script":
				continue

			# Build command line with parameters
			cmd_line = cmd_state.command_name
			if cmd_state.command_params:
				formatted_params = self.common.format_parameters_for_display(
					cmd_state.command_name, cmd_state.command_params
				)
				param_parts = []
				for key, value in formatted_params.items():
					if isinstance(value, str):
						# String values - always add quotes for safety
						# (names can contain spaces, making quotes necessary)
						param_parts.append(f'{key}="{value}"')
					elif isinstance(value, (list, dict)):
						# Lists and dicts - write as Python literals
						param_parts.append(f'{key}={value}')
					else:
						# Numbers, booleans, etc.
						param_parts.append(f'{key}={value}')
				params_str = " ".join(param_parts)
				cmd_line = f"{cmd_line} {params_str}"
			script_lines.append(cmd_line)

		table_widget = QTableWidget(len(script_lines), 1)
		#
		for each_row, cmd in enumerate(script_lines):
			table_widget.setItem(each_row, 0, QTableWidgetItem(cmd))
		return table_widget

	# ------------------------------------------------------------------------
