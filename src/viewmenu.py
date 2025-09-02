
# import numpy as np
import pandas as pd
import peek

from PySide6.QtWidgets import (
	QTableWidget, QTableWidgetItem, QTextEdit
)

# Local application imports

from common import Spaces
from director import Status
from exceptions import SpacesError

# ------------------------------------------------------------------------


class HistoryCommand:
	""" The History command displays the commands used in
	this session.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		director.command = "History"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._print_history()
		self._director.title_for_table_widget = "Commands used"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

		# --------------------------------------------------------------------

	def _print_history(self) -> None:

		commands_used = self._director.commands_used
		command_exit_code = self._director.command_exit_code

		line = "\n\t"
		print("\n\tCommands used")
		range_commands_used = range(1, len(commands_used))
		for i in range_commands_used:
			line = line + commands_used[i] + "\t"
			if command_exit_code[i] == 0:
				line = line + "Completed successfully"
			elif i < (len(commands_used) - 1):
				line = line + "Failed"
			else:
				line = line + "In process"
			print(line)
			line = "\t"
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_history()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Command", "Status"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

# ------------------------------------------------------------------------

	def _create_table_widget_for_history_initialize_variables(
			self) -> None:

		self.unknown_status_of_command_error_title = "History"
		self.unknown_status_of_command_error_message = (
			"Commands used has unknown value")


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
				each_command, 0,
				QTableWidgetItem(commands_used[each_command]))
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
						self.unknown_status_of_command_error_message)
			#
			table_widget.setItem(
				each_command, 1, QTableWidgetItem(status_str))
		return table_widget


	# ------------------------------------------------------------------------


class ViewConfigurationCommand:
	""" The View configuration command displays the active configuration .
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View configuration"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_configuration()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"configuration")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewCorrelationsCommand:
	""" The View correlations command presents correlations
	among evaluations. These can be used as similarities
	for multidimensional scaling
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View correlations"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# common.print_lower_triangle(self._director.correlations_active)
		self._director.correlations_active.print_the_correlations(
			self._director.common.width,
			self._director.common.decimals, common)
		# self._director.correlations_active)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_corr")
		nreferent = self._director.correlations_active.nreferent
		self._director.title_for_table_widget = \
			f"Correlation matrix has {nreferent} items"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return


	# ------------------------------------------------------------------------


class ViewCustomCommand:
	""" The View custom command displays the active configuration
	using custom ranges on the dimensions.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View custom"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._print_view_custom()
		self.\
			_create_view_custom_plot_for_plot_and_gallery_tabs_using_matplotlib()
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_view_custom(self) -> None:

		npoint = self._director.configuration_active.npoint
		ndim = self._director.configuration_active.ndim

		print(
			"\n\tConfiguration has", ndim, "dimensions and", npoint,
			"points\n")
		self._director.configuration_active.print_active_function()
		return


	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget | QTextEdit:
		#

		dim_names = self._director.configuration_active.dim_names
		point_names = self._director.configuration_active.point_names
		point_coords = self._director.configuration_active.point_coords

		gui_output_as_widget = \
			self._create_table_widget_from_config(point_coords)
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget, dim_names, point_names)
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
					each_point, each_dim, QTableWidgetItem(value))
		return table_widget

	# ------------------------------------------------------------------------


class ViewDistancesCommand:
	""" View distances command - displays a matrix of inter-point distances.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View distances"
		self._width = 8
		self._decimals = 2
		self._director.configuration_active.nreferent \
			= self._director.configuration_active.npoint
		self._director.title_for_table_widget = "Inter-point distances"
		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.inter_point_distances()
		self._director.configuration_active.print_the_distances(
			self._width, self._decimals, common)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_dist")
		self._director.title_for_table_widget = "Inter-point distances"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return


	# ------------------------------------------------------------------------


class ViewEvaluationsCommand:
	""" The View evaluations command displays the active evaluations.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View evaluations"
		self._director.width = 8
		self._director.decimals = 2

		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"evaluations")
		self._director.title_for_table_widget = "Evaluations"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return


	# ------------------------------------------------------------------------


class ViewGroupedDataCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		director.command = "View grouped data"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		ndim = self._director.grouped_data_candidate.ndim
		ngroups = self._director.grouped_data_candidate.ngroups
		
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.grouped_data_active.print_grouped_function()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"grouped_data")
		grouping_var = self._director.grouped_data_active.grouping_var
		self._director.title_for_table_widget = (
			f"Configuration is based on {grouping_var}"
			f" and has {ndim} dimensions and {ngroups} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return


	# ------------------------------------------------------------------------


class ViewIndividualsCommand:
	""" The View individuals command displays the active individuals.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View individuals"
		self._director.width = 8
		self._director.decimals = 2

		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.individuals_active.print_individuals()
		# self._director.common.create_plot_for_plot_and_gallery_tabs(
		# "individuals")
		self._director.title_for_table_widget = "Individuals"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewPointUncertaintyCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		"""The View Point Uncertainty Command....
		"""
		self._director = director
		self.common = common
		self._director.command = "View point uncertainty"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces, # noqa: ARG002
			plot_to_show: str) -> None:

		peek("At top of ViewPointUncertaintyCommand.execute()"
			" - self._director.uncertainty_active.sample_solutions: ",
			f"{self._director.uncertainty_active.sample_solutions}")
		self.plot_to_show = plot_to_show

		director = self._director
		common = self.common
		uncertainty_active = director.uncertainty_active
		target_active = director.target_active
		sample_solutions = uncertainty_active.sample_solutions
		point_names = target_active.point_names

		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()
		focal_index = common.get_focal_item_from_user(
			"Point uncertainty",
			"Select point to view uncertainty",
			point_names)
		self._focal_item_index = focal_index
		common.create_plot_for_plot_and_gallery_tabs("configuration")
		self._director.title_for_table_widget = (
			f"Uncertainty of location of {point_names[focal_index]} ")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return
	# ------------------------------------------------------------------------


class ViewSampleDesignCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The View Sample design command is used to view a sample design.
		"""
		self._director = director
		self.common = common
		self._director.command = "View sample design"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		peek("At top of ViewSampleDesignCommand.execute()"
			" - self._director.uncertainty_active.sample_design: ",
			f"{self._director.uncertainty_active.sample_design}")
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		sample_design = self._director.uncertainty_active.sample_design
		print(sample_design)
		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = \
			self._director.uncertainty_active.probability_of_inclusion
		self._director.title_for_table_widget = \
			(f"Sample design - Size of universe: {universe_size},"
				f" Probability of inclusion: "
				f"{probability_of_inclusion}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = \
			self._director.uncertainty_active. \
			create_table_widget_for_sample_designer()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Repetition", "Selected \n N", "Percent", "Not selected \n N",
				"Percent"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

#  --------------------------------------------------------------------------


class ViewSampleRepetitionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The View Sample repetitions command is used to view sample
		repetitions.
		"""
		self._director = director
		self.common = common
		self._director.command = "View sample repetitions"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		print(self._director.uncertainty_active.sample_repetitions)
		self._director.title_for_table_widget = "Sample repetitions"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
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
			["Repetition", "Selected \n N", "Percent", "Not selected \n N",
				"Percent"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

#  --------------------------------------------------------------------------


class ViewSampleSolutionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The View Sample Solutions command is used to view sample solutions.
		"""
		self._director = director
		self.common = common
		self._director.command = "View sample solutions"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		print(self._director.uncertainty_active.sample_solutions)
		self._director.title_for_table_widget = "Sample solutions"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
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
			["Repetition", "Selected \n N", "Percent", "Not selected \n N",
				"Percent"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------


class ViewScoresCommand:
	""" The View scores command displays the active scores.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		director.command = "View scores"
		self._width = 8
		self._decimals = 2
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		nscores = self._director.scores_active.nscores
		nscored = self._director.scores_active.nscored_individ

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.title_for_table_widget = (
			f"There are {nscores} active scores for {nscored} "
			f"individuals.")
		self._director.common.create_plot_for_plot_and_gallery_tabs("scores")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewSimilaritiesCommand:
	""" The View similarities command is used to display similarities
	between the points.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View similarities"
		self._width = 8
		self._decimals = 2
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		value_type = self._director.similarities_active.value_type
		nreferent = self._director.similarities_active.nreferent

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common)
		self._director.title_for_table_widget = (
			f"The {value_type} matrix has {nreferent} items")
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_simi")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return


	# ------------------------------------------------------------------------


class ViewSpatialUncertaintyCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The View Spatial Uncertainty Command....
		"""
		self._director = director
		self.common = common
		self._director.command = "View spatial uncertainty"

		return


	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces, # noqa: ARG002
			plot_to_show: str) -> None:

		peek("At top of ViewSpatialUncertaintyCommand.execute()"
			" - self._director.uncertainty_active.sample_solutions: ",
			f"{self._director.uncertainty_active.sample_solutions}")
		self.plot_to_show = plot_to_show
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		sample_solutions = self._director.uncertainty_active.sample_solutions
		print(sample_solutions)
		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = \
			self._director.uncertainty_active.probability_of_inclusion
		self._director.title_for_table_widget = \
			(f"Spatial Uncertainty??????? - Size of universe: {universe_size},"
				f" Probability of inclusion: "
				f"{probability_of_inclusion}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return
	
	# ------------------------------------------------------------------------


class ViewTargetCommand:
	""" The View target command displays the target configuration .
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "View target"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		ndim = self._director.target_active.ndim
		npoint = self._director.target_active.npoint
		
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.target_active.print_target()
		self._director.common.create_plot_for_plot_and_gallery_tabs("target")
		self._director.title_for_table_widget = (
			f"Target configuration has {ndim}"
			f" dimensions and {npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ViewUncertaintyCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The View Uncertainty Command....
		"""
		self._director = director
		self.common = common
		self._director.command = "View uncertainty"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		nscores = self._director.scores_active.nscores
		nscored = self._director.scores_active.nscored_individ

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.common.create_plot_for_plot_and_gallery_tabs("scores")
		self._director.title_for_table_widget = (
			f"There are {nscores} active "
			f"scores for {nscored} individuals.")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

