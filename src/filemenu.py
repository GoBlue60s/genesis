from __future__ import annotations

# Standard library imports
import sys
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING
# from dialogs import (  # noqa: PLC0415
# 	GetIntegerDialog,
# 	GetStringDialog,
# 	GetCoordinatesDialog,
# )
import pandas as pd

if TYPE_CHECKING:
	from director import Spaces
	from director import Status

from exceptions import SpacesError
from rivalry import Rivalry

if __name__ == "__main__":  # pragma: no cover
	print(f"This module is not designed to run as a script.  {Path(__file__).name}")
	sys.exit(1)


# ----------------------------------------------------------------------------


class ConfigurationCommand:
	"""The Configuration command is used to open a configuration file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Configuration"
		self._config_caption = "Open configuration"
		self._config_filter = "*.txt"
		self._config_error_bad_input_title = "Configuration problem"
		self._config_error_bad_input_message = (
			"Input is inconsistent with a "
			"configuration file.\nLook at the contents of file and try "
			"again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._config_caption, self._config_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Configuration", "active", params
		)

		# Read and validate configuration file
		self._director.configuration_candidate = common.read_configuration_type_file(
			file_name, "Configuration"
		)

		self._director.configuration_active = (
			self._director.configuration_candidate
		)
		self._director.configuration_original = (
			self._director.configuration_active
		)
		self._director.configuration_last = self._director.configuration_active

		# Eliminate rivalry when new configuration is loaded
		self._director.rivalry = Rivalry(self._director)

		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		ndim = self._director.configuration_candidate.ndim
		npoint = self._director.configuration_candidate.npoint
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class CorrelationsCommand:
	"""The Correlations command is used to read a correlations file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Correlations"
		self._correlations_caption = "Open correlations"
		self._correlations_filter = "*.txt"
		self._correlations_error_bad_input_title = "Correlations problem"
		self._correlations_error_bad_input_message = (
			"Input is inconsistent with a correlations file.\nLook "
			"at the contents of file and try again."
		)
		self._correlations_error_title = "Correlations inconsistency"
		self._correlations_error_message = (
			"There are inconsistencies "
			"with the correlations file.\n"
			"Please check the file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._correlations_caption, self._correlations_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Correlations", "active", params
		)

		# Error handling
		# If not a correlations file, then return an error message
		try:
			self._read_correlations(file_name, common)
		except ValueError as e:
			raise SpacesError(
				self._correlations_error_bad_input_title,
				self._correlations_error_bad_input_message,
			) from e

		# Check for consistency between correlations and active configuration
		self._director.dependency_checker.detect_consistency_issues()

		self._director.correlations_active = (
			self._director.correlations_candidate
		)
		self._director.correlations_original = (
			self._director.correlations_active
		)
		self._director.correlations_last = self._director.correlations_active
		self._director.correlations_active.print_the_correlations(
			width=8,
			decimals=3,
			common=common,
		)
		self._director.common.create_plot_for_tabs("heatmap_corr")
		self._director.title_for_table_widget = (
			"The correlations are shown as a square matrix"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_correlations(self, file_name: str, common: Spaces) -> None:
		"""Read correlations from lower triangular file and store in candidate.

		Correlations are stored in a lower triangular matrix format, which is
		different from the rectangular format used for evaluations.
		"""
		try:
			# Use the existing read_lower_triangular_matrix function
			self._director.correlations_candidate = (
				common.read_lower_triangular_matrix(file_name, "correlations")
			)

			# Duplicate correlations to create all required formats
			self._director.correlations_candidate.duplicate_correlations(common)

		except (
			FileNotFoundError,
			PermissionError,
		) as e:
			raise ValueError(f"Unable to read correlations file: {e}") from e

	# ------------------------------------------------------------------------


class CreateCommand:
	"""The Create command is used to create a new configuration interactively."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Create"
		self._director.title_for_table_widget = "Create configuration"
		self._number_of_points_title = "Specify the number of points"
		self._number_of_points_message = (
			"Enter the number of points in the configuration:"
		)
		self._number_of_dimensions_title = "Specify the number of dimensions"
		self._number_of_dimensions_message = (
			"Enter the number of dimensions in the configuration:"
		)
		self._labels_title = "Specify the labels"
		self._labels_message = "Enter a label for "
		self._names_title = "Specify the names"
		self._names_message = "Enter a name for "
		self._coordinates_title = "Specify the coordinates"
		self._coordinates_message = "Enter coordinates for "
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:

		from dialogs import (  # noqa: PLC0415
			GetIntegerDialog,
			GetStringDialog,
			GetCoordinatesDialog,
		)
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get number of points from user
		npoint_dialog = GetIntegerDialog(
			self._number_of_points_title,
			self._number_of_points_message,
			min_value=2,
			max_value=100,
		)
		if not npoint_dialog.exec():
			raise SpacesError(
				"Create cancelled", "Configuration creation was cancelled"
			)
		npoint = npoint_dialog.get_value()

		# Get number of dimensions from user
		ndim_dialog = GetIntegerDialog(
			self._number_of_dimensions_title,
			self._number_of_dimensions_message,
			min_value=2,
			max_value=10,
		)
		if not ndim_dialog.exec():
			raise SpacesError(
				"Create cancelled", "Configuration creation was cancelled"
			)
		ndim = ndim_dialog.get_value()

		# Get point labels and names
		point_labels = []
		point_names = []
		for each_point in range(npoint):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}point {each_point + 1}:",
			)
			if not label_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Configuration creation was cancelled"
				)
			point_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}point {each_point + 1}:",
			)
			if not name_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Configuration creation was cancelled"
				)
			point_names.append(name_dialog.get_value())

		# Get dimension labels and names
		dim_labels = []
		dim_names = []
		for each_dim in range(ndim):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}dimension {each_dim + 1}:",
			)
			if not label_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Configuration creation was cancelled"
				)
			dim_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}dimension {each_dim + 1}:",
			)
			if not name_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Configuration creation was cancelled"
				)
			dim_names.append(name_dialog.get_value())

		# Get coordinates for each point
		coords_data = []
		for each_point in range(npoint):
			coords_dialog = GetCoordinatesDialog(
				self._coordinates_title,
				f"{self._coordinates_message}{point_names[each_point]}:",
				ndim,
			)
			if not coords_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Configuration creation was cancelled"
				)
			coords = coords_dialog.get_values()
			coords_data.append(coords)

		# Create DataFrame with proper labels
		point_coords = pd.DataFrame(
			coords_data, index=point_labels, columns=dim_labels
		)

		# Capture state for undo BEFORE modifications
		params = {"npoint": npoint, "ndim": ndim}
		self.common.capture_and_push_undo_state("Create", "active", params)

		# Store the new configuration
		self._director.configuration_candidate.ndim = ndim
		self._director.configuration_candidate.npoint = npoint
		self._director.configuration_candidate.range_dims = range(ndim)
		self._director.configuration_candidate.range_points = range(npoint)
		self._director.configuration_candidate.dim_labels = dim_labels
		self._director.configuration_candidate.dim_names = dim_names
		self._director.configuration_candidate.point_labels = point_labels
		self._director.configuration_candidate.point_names = point_names
		self._director.configuration_candidate.point_coords = point_coords

		self._director.configuration_active = (
			self._director.configuration_candidate
		)
		self._director.configuration_original = (
			self._director.configuration_active
		)
		self._director.configuration_last = self._director.configuration_active
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class DeactivateCommand:
	"""The Deactivate command is used to clear active features."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Deactivate"
		self._director.title_for_table_widget = "Deactivate"
		self._deactivate_items_title = "Select items to deactivate"
		self._deactivate_items_message = "Select one or more items to deactivate:"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		from dialogs import GetCheckboxListDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Build list of active features
		available_items = []
		descriptions = []

		if self._director.configuration_active.ndim > 0:
			available_items.append("Configuration")
			descriptions.append(
				f"ndim={self._director.configuration_active.ndim}, "
				f"npoint={self._director.configuration_active.npoint}"
			)

		if len(self._director.correlations_active.correlations) > 0:
			available_items.append("Correlations")
			descriptions.append(
				f"nvar={self._director.correlations_active.nvar}"
			)

		if not self._director.evaluations_active.evaluations.empty:
			available_items.append("Evaluations")
			descriptions.append(
				f"rows={len(self._director.evaluations_active.evaluations)}"
			)

		if self._director.grouped_data_active.ngroups > 0:
			available_items.append("Grouped data")
			descriptions.append(
				f"ngroups={self._director.grouped_data_active.ngroups}"
			)

		if not self._director.individuals_active.ind_vars.empty:
			available_items.append("Individuals")
			descriptions.append(
				f"rows={len(self._director.individuals_active.ind_vars)}"
			)

		if not self._director.scores_active.scores.empty:
			available_items.append("Scores")
			descriptions.append(
				f"rows={len(self._director.scores_active.scores)}"
			)

		if len(self._director.similarities_active.similarities) > 0:
			available_items.append("Similarities")
			descriptions.append(
				f"nvar={self._director.similarities_active.nvar}"
			)

		if self._director.target_active.ndim > 0:
			available_items.append("Target")
			descriptions.append(
				f"ndim={self._director.target_active.ndim}, "
				f"npoint={self._director.target_active.npoint}"
			)

		if len(available_items) == 0:
			raise SpacesError(
				"Nothing to deactivate",
				"There are no active features to deactivate.",
			)

		# Get user selection
		dialog = GetCheckboxListDialog(
			self._deactivate_items_title,
			self._deactivate_items_message,
			available_items,
			descriptions,
		)

		if not dialog.exec():
			msg_title = "Deactivate cancelled"
			msg = "Deactivation was cancelled"
			raise SpacesError(msg_title, msg)

		selected_items = dialog.get_selected_items()

		if len(selected_items) == 0:
			raise SpacesError(
				"Nothing selected",
				"No items were selected for deactivation.",
			)

		# Capture state for undo BEFORE modifications
		# Conditional: captures state for each item user selects to deactivate
		params = {"items": selected_items}
		self.common.capture_and_push_undo_state("Deactivate", "active", params)

		# Deactivate selected items
		deactivated_list = []
		for item in selected_items:
			if item == "Configuration":
				self._director.abandon_configuration()
				deactivated_list.append("Configuration")
			elif item == "Correlations":
				self._director.abandon_correlations()
				deactivated_list.append("Correlations")
			elif item == "Evaluations":
				self._director.abandon_evaluations()
				deactivated_list.append("Evaluations")
			elif item == "Grouped data":
				self._director.abandon_grouped_data()
				deactivated_list.append("Grouped data")
			elif item == "Individuals":
				self._director.abandon_individual_data()
				deactivated_list.append("Individuals")
			elif item == "Scores":
				self._director.abandon_scores()
				deactivated_list.append("Scores")
			elif item == "Similarities":
				self._director.abandon_similarities()
				deactivated_list.append("Similarities")
			elif item == "Target":
				self._director.abandon_target()
				deactivated_list.append("Target")

		# Store deactivated items for potential undo
		self._director.deactivated_items = deactivated_list
		self._director.deactivated_descriptions = descriptions

		# Display confirmation
		deactivated_items_str = ", ".join(deactivated_list)
		self._director.title_for_table_widget = (
			f"Deactivated: {deactivated_items_str}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class EvaluationsCommand:
	"""The Evaluations command is used to read an evaluations file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Evaluations"
		self._evaluations_caption = "Open evaluations"
		self._evaluations_filter = "*.csv"
		self._evaluations_error_bad_input_title = "Evaluations problem"
		self._evaluations_error_bad_input_message = (
			"Input is inconsistent with an evaluations file.\nLook at "
			"the contents of file and try again."
		)
		self._evaluations_error_title = "Evaluations inconsistency"
		self._evaluations_error_message = (
			"There are inconsistencies with the evaluations file.\n"
			"Please check the file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self.common.capture_and_push_undo_state("Evaluations", "active", {})
		file_name: str = self._get_file_name()
		self._read_evaluations(file_name)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.evaluations_active = (
			self._director.evaluations_candidate
		)
		self._director.evaluations_original = (
			self._director.evaluations_active
		)
		self._director.evaluations_last = self._director.evaluations_active
		self._compute_correlations_from_evaluations(common)
		self._director.evaluations_active.print_the_evaluations()
		self._director.evaluations_active.summarize_evaluations()
		self._director.common.create_plot_for_tabs("evaluations")
		self._director.title_for_table_widget = (
			"Evaluations have been read and correlations computed"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_file_name(self) -> str:
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			return self._director.script_parameters["file_name"]
		return self._director.get_file_name_and_handle_nonexistent_file_names(
			self._evaluations_caption, self._evaluations_filter
		)

	# ------------------------------------------------------------------------

	def _read_evaluations(self, file_name: str) -> None:
		try:
			evaluations = pd.read_csv(file_name)
			(nevaluators, nreferent) = evaluations.shape
			nitem = nreferent
			range_items = range(nreferent)
			item_names = evaluations.columns.tolist()
			item_labels = [label[0:4] for label in item_names]

			if len(item_names) < 3:
				raise ValueError("Evaluations file must have at least 3 items")

			self._director.evaluations_candidate.evaluations = evaluations
			self._director.evaluations_candidate.nevaluators = nevaluators
			self._director.evaluations_candidate.nreferent = nreferent
			self._director.evaluations_candidate.nitem = nitem
			self._director.evaluations_candidate.range_items = range_items
			self._director.evaluations_candidate.item_names = item_names
			self._director.evaluations_candidate.item_labels = item_labels
			self._director.evaluations_candidate.file_handle = file_name

		except (
			FileNotFoundError,
			PermissionError,
			pd.errors.EmptyDataError,
			pd.errors.ParserError,
			ValueError,
		) as e:
			raise SpacesError(
				self._evaluations_error_bad_input_title,
				self._evaluations_error_bad_input_message,
			) from e

	# ------------------------------------------------------------------------

	def _compute_correlations_from_evaluations(
		self, common: Spaces
	) -> None:
		"""Compute correlations from evaluations data."""
		nreferent = self._director.evaluations_active.nreferent
		item_names = self._director.evaluations_active.item_names
		item_labels = self._director.evaluations_active.item_labels
		evaluations = self._director.evaluations_active.evaluations

		correlations_as_dataframe = evaluations.corr(method="pearson")

		correlations = []
		for each_col in range(1, nreferent):
			a_row = []
			for each_row in range(each_col):
				a_row.append(correlations_as_dataframe.iloc[each_row, each_col])
			correlations.append(a_row)

		self._director.correlations_candidate.nreferent = nreferent
		self._director.correlations_candidate.nitem = nreferent
		self._director.correlations_candidate.item_names = item_names
		self._director.correlations_candidate.item_labels = item_labels
		self._director.correlations_candidate.correlations = correlations
		self._director.correlations_candidate.correlations_as_dataframe = (
			correlations_as_dataframe
		)
		self._director.correlations_candidate.duplicate_correlations(common)
		self._director.correlations_candidate.ndyad = len(
			self._director.correlations_candidate.correlations_as_list
		)
		self._director.correlations_candidate.n_pairs = len(
			self._director.correlations_candidate.correlations_as_list
		)
		self._director.correlations_candidate.range_dyads = range(
			self._director.correlations_candidate.ndyad
		)

		self._director.correlations_active = (
			self._director.correlations_candidate
		)
		self._director.correlations_original = (
			self._director.correlations_active
		)
		self._director.correlations_last = self._director.correlations_active

	# ------------------------------------------------------------------------


class ExitCommand:
	"""The Exit command is used to exit the application."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Exit"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.record_command_as_successfully_completed()
		sys.exit(0)

	# ------------------------------------------------------------------------


class GroupedDataCommand:
	"""The Grouped data command is used to read a grouped data file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Grouped data"
		self._grouped_data_caption = "Open grouped data"
		self._grouped_data_filter = "*.txt"
		self._grouped_data_error_bad_input_title = "Grouped data problem"
		self._grouped_data_error_bad_input_message = (
			"Input is inconsistent with a grouped data file.\nLook at the "
			"contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._grouped_data_caption, self._grouped_data_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Grouped data", "active", params
		)

		# Error handling
		# If not a grouped data file, then return an error message
		try:
			self._read_grouped_data(file_name)
		except ValueError as e:
			raise SpacesError(
				self._grouped_data_error_bad_input_title,
				self._grouped_data_error_bad_input_message,
			) from e

		self._director.grouped_data_active = (
			self._director.grouped_data_candidate
		)
		self._director.grouped_data_original = (
			self._director.grouped_data_active
		)
		self._director.grouped_data_last = self._director.grouped_data_active
		self._director.grouped_data_active.print_grouped_data()
		self._director.common.create_plot_for_tabs("grouped_data")
		ndim = self._director.grouped_data_candidate.ndim
		ngroups = self._director.grouped_data_candidate.ngroups
		self._director.title_for_table_widget = (
			f"Grouped data has {ndim} dimensions and {ngroups} groups"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_grouped_data_initialized_variables(
		self, file_name: str, file_handle: str
	) -> None:
		self.grouped_data_file_not_found_error_title = "Grouped data"
		self.grouped_data_file_not_found_error_message = (
			f"File not found: \n{file_name}"
		)
		self.grouped_data_file_not_found_error_title = "Grouped data"
		self.grouped_data_empty_header_error_message = (
			f"The header line is empty in file:.\n{file_handle}"
		)
		self.grouped_data_file_not_grouped_error_title = "Grouped data"
		self.grouped_data_file_not_grouped_error_message = (
			f"File is not a grouped data file:\n{file_handle}"
		)
		self.missing_grouping_var_error_title = "Grouped data"
		self.missing_grouping_var_error_message = (
			f"Line for grouping variable name is empty in file: \n{file_handle}"
		)
		self.group_data_file_not_found_error_title = "Grouped data"
		self.group_data_file_not_found_error_message = (
			f"File not found: \n{file_handle}"
		)

	# ------------------------------------------------------------------------

	def _read_grouped_data(self, file_name: str) -> None:
		"""Read groups - is used by group command needing to read
		a group configuration from a file.
		"""
		file_handle = self._director.grouped_data_candidate.file_handle

		self._read_grouped_data_initialized_variables(file_name, file_handle)

		dim_names = []
		dim_labels = []
		group_names = []
		group_labels = []
		group_codes = []
		try:
			with Path(file_name).open() as file_handle:
				header = file_handle.readline()
				if len(header) == 0:
					raise SpacesError(
						self.grouped_data_file_not_found_error_title,
						self.grouped_data_file_not_found_error_message,
					) from None

				if header.lower().strip() != "grouped":
					raise SpacesError(
						self.grouped_data_file_not_grouped_error_title,
						self.grouped_data_file_not_grouped_error_message,
					) from None

				grouping_var = file_handle.readline()
				if len(grouping_var) == 0:
					raise SpacesError(
						self.missing_grouping_var_error_title,
						self.missing_grouping_var_error_message,
					) from None
				grouping_var = grouping_var.strip("\n")
				dim = file_handle.readline()
				dim_list = dim.strip("\n").split()
				expected_dim = int(dim_list[0])
				expected_groups = int(dim_list[1])
				range_groups = range(expected_groups)
				range_dims = range(expected_dim)
				for _ in range(expected_dim):
					(dim_label, dim_name) = file_handle.readline().split(";")
					dim_labels.append(dim_label)
					dim_name = dim_name.strip("\n")
					dim_names.append(dim_name)
				for i in range(expected_groups):
					(group_label, group_code, group_name) = (
						file_handle.readline().split(";")
					)
					group_names.append(group_name)
					group_labels.append(group_label)
					group_codes.append(group_code)

					group_names[i] = group_names[i].strip()
				group_coords = pd.DataFrame(
					[
						[float(g) for g in file_handle.readline().split()]
						for i in range(expected_groups)
					],
					index=group_names,
					columns=dim_labels,
				)
		except FileNotFoundError:
			raise SpacesError(
				self.group_data_file_not_found_error_title,
				self.group_data_file_not_found_error_message,
			) from None

		self._director.grouped_data_candidate.grouping_var = grouping_var
		self._director.grouped_data_candidate.ndim = expected_dim
		self._director.grouped_data_candidate.dim_names = dim_names
		self._director.grouped_data_candidate.dim_labels = dim_labels
		self._director.grouped_data_candidate.npoint = expected_groups
		self._director.grouped_data_candidate.ngroups = expected_groups
		self._director.grouped_data_candidate.range_groups = range_groups
		self._director.grouped_data_candidate.group_names = group_names
		self._director.grouped_data_candidate.group_labels = group_labels
		self._director.grouped_data_candidate.group_codes = group_codes
		self._director.grouped_data_candidate.group_coords = group_coords
		self._director.grouped_data_candidate.range_dims = range_dims

		return

	# ------------------------------------------------------------------------


class IndividualsCommand:
	"""The Individuals command is used to read an individuals file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Individuals"
		self._individuals_caption = "Open individuals"
		self._individuals_filter = "*.csv"
		self._individuals_error_bad_input_title = "Individuals problem"
		self._individuals_error_bad_input_message = (
			"Input is inconsistent with an individuals file.\nLook at "
			"the contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._individuals_caption, self._individuals_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Individuals", "active", params
		)

		# Error handling
		# If not an individuals file, then return an error message
		try:
			common.read_individuals_file_check_for_errors_store_as_candidate(
				file_name, self._director.individuals_candidate
			)
		except ValueError as e:
			raise SpacesError(
				self._individuals_error_bad_input_title,
				self._individuals_error_bad_input_message,
			) from e

		self._director.individuals_active = (
			self._director.individuals_candidate
		)
		self._director.individuals_original = (
			self._director.individuals_active
		)
		self._director.individuals_last = self._director.individuals_active
		self._director.individuals_active.print_individuals()
		self._director.title_for_table_widget = (
			f"Individuals data has been read "
			f"({len(self._director.individuals_active.ind_vars)} rows)"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class NewGroupedDataCommand:
	"""The New grouped data command is used to create a new grouped data file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "New grouped data"
		self._director.title_for_table_widget = "Create grouped data"
		self._group_title = "Grouping variable"
		self._group_label = "Enter name of grouping variable"
		self._group_default = {"Grouping variable"}
		self._group_max_chars = 32
		self._number_of_groups_title = "Specify the number of groups"
		self._number_of_groups_message = (
			"Enter the number of groups in the grouped data:"
		)
		self._number_of_dimensions_title = "Specify the number of dimensions"
		self._number_of_dimensions_message = (
			"Enter the number of dimensions in the grouped data:"
		)
		self._labels_title = "Specify the labels"
		self._labels_message = "Enter a label for "
		self._names_title = "Specify the names"
		self._names_message = "Enter a name for "
		self._coordinates_title = "Specify the coordinates"
		self._coordinates_message = "Enter coordinates for "
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		from dialogs import (  # noqa: PLC0415
			GetIntegerDialog,
			GetStringDialog,
			GetCoordinatesDialog,
		)

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_grouping_var()

		# Get number of groups from user
		ngroups_dialog = GetIntegerDialog(
			self._number_of_groups_title,
			self._number_of_groups_message,
			min_value=2,
			max_value=100,
		)
		if not ngroups_dialog.exec():
			raise SpacesError(
				"Create cancelled", "Grouped data creation was cancelled"
			)
		ngroups = ngroups_dialog.get_value()

		# Get number of dimensions from user
		ndim_dialog = GetIntegerDialog(
			self._number_of_dimensions_title,
			self._number_of_dimensions_message,
			min_value=2,
			max_value=10,
		)
		if not ndim_dialog.exec():
			raise SpacesError(
				"Create cancelled", "Grouped data creation was cancelled"
			)
		ndim = ndim_dialog.get_value()

		# Get group labels and names
		group_labels = []
		group_names = []
		group_codes = []
		for each_group in range(ngroups):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}group {each_group + 1}:",
			)
			if not label_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Grouped data creation was cancelled"
				)
			group_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}group {each_group + 1}:",
			)
			if not name_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Grouped data creation was cancelled"
				)
			group_names.append(name_dialog.get_value())
			# Generate sequential group codes starting from 1
			group_codes.append(str(each_group + 1))

		# Get dimension labels and names
		dim_labels = []
		dim_names = []
		for each_dim in range(ndim):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}dimension {each_dim + 1}:",
			)
			if not label_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Grouped data creation was cancelled"
				)
			dim_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}dimension {each_dim + 1}:",
			)
			if not name_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Grouped data creation was cancelled"
				)
			dim_names.append(name_dialog.get_value())

		# Get coordinates for each group
		coords_data = []
		for each_group in range(ngroups):
			coords_dialog = GetCoordinatesDialog(
				self._coordinates_title,
				f"{self._coordinates_message}{group_names[each_group]}:",
				ndim,
			)
			if not coords_dialog.exec():
				raise SpacesError(
					"Create cancelled", "Grouped data creation was cancelled"
				)
			coords = coords_dialog.get_values()
			coords_data.append(coords)

		# Create DataFrame with proper labels
		group_coords = pd.DataFrame(
			coords_data, index=group_names, columns=dim_labels
		)

		# Capture state for undo BEFORE modifications
		params = {"ngroups": ngroups, "ndim": ndim}
		self.common.capture_and_push_undo_state(
			"New grouped data", "active", params
		)

		# Store the new grouped data
		self._director.grouped_data_candidate.ndim = ndim
		self._director.grouped_data_candidate.ngroups = ngroups
		self._director.grouped_data_candidate.range_dims = range(ndim)
		self._director.grouped_data_candidate.range_groups = range(ngroups)
		self._director.grouped_data_candidate.dim_labels = dim_labels
		self._director.grouped_data_candidate.dim_names = dim_names
		self._director.grouped_data_candidate.group_labels = group_labels
		self._director.grouped_data_candidate.group_names = group_names
		self._director.grouped_data_candidate.group_codes = group_codes
		self._director.grouped_data_candidate.group_coords = group_coords

		self._director.grouped_data_active = (
			self._director.grouped_data_candidate
		)
		self._director.grouped_data_original = (
			self._director.grouped_data_active
		)
		self._director.grouped_data_last = self._director.grouped_data_active
		self._director.grouped_data_active.print_grouped_data()
		self._director.common.create_plot_for_tabs("grouped_data")
		self._director.title_for_table_widget = (
			f"Grouped data has {ndim} dimensions and {ngroups} groups"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_grouping_var_initialize_variables(self) -> None:
		self.missing_grouping_var_error_title = "New grouped data configuration"
		self.missing_grouping_var_error_message = (
			"Need name of grouping variable for "
			"new grouped data configuration"
		)

	# ------------------------------------------------------------------------

	def _get_grouping_var(self) -> None:
		from dialogs import SetNamesDialog  # noqa: PLC0415

		self._get_grouping_var_initialize_variables()
		group_title = self._group_title
		group_label = self._group_label
		group_default = self._group_default
		group_max_chars = self._group_max_chars

		dialog = SetNamesDialog(
			group_title, group_label, group_default, group_max_chars
		)
		if dialog.exec():
			group_var_list = dialog.getNames()
			grouping_var = group_var_list[0]
		else:
			raise SpacesError(
				self.missing_grouping_var_error_title,
				self.missing_grouping_var_error_message,
			)

		self._director.grouped_data_candidate.grouping_var = grouping_var
		return

	# ------------------------------------------------------------------------


class OpenSampleDesignCommand:
	"""The Open sample design command is used to read a sample design file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Open sample design"
		self._sample_design_caption = "Open sample design"
		self._sample_design_filter = "*.txt"
		self._sample_design_error_bad_input_title = "Sample design problem"
		self._sample_design_error_bad_input_message = (
			"Input is inconsistent with a sample design file.\nLook at "
			"the contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._sample_design_caption, self._sample_design_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Open sample design", "active", params
		)

		# Error handling
		# If not a sample design file, then return an error message
		try:
			common.read_sample_design_file_check_for_errors(
				file_name, self._director.uncertainty_active
			)
		except ValueError as e:
			raise SpacesError(
				self._sample_design_error_bad_input_title,
				self._sample_design_error_bad_input_message,
			) from e

		self._director.uncertainty_active.print_sample_design()
		self._director.title_for_table_widget = (
			"Sample design has been read"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class OpenSampleRepetitionsCommand:
	"""The Open sample repetitions command is used to read sample repetitions."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Open sample repetitions"
		self._sample_repetitions_caption = "Open sample repetitions"
		self._sample_repetitions_filter = "*.txt"
		self._sample_repetitions_error_bad_input_title = (
			"Sample repetitions problem"
		)
		self._sample_repetitions_error_bad_input_message = (
			"Input is inconsistent with a sample repetitions file.\nLook at "
			"the contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._sample_repetitions_caption, self._sample_repetitions_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Open sample repetitions", "active", params
		)

		# Error handling
		# If not a sample repetitions file, then return an error message
		try:
			common.read_sample_repetitions_file_check_for_errors(
				file_name, self._director.uncertainty_active
			)
		except ValueError as e:
			raise SpacesError(
				self._sample_repetitions_error_bad_input_title,
				self._sample_repetitions_error_bad_input_message,
			) from e

		self._director.uncertainty_active.print_sample_repetitions()
		self._director.title_for_table_widget = (
			"Sample repetitions have been read"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class OpenSampleSolutionsCommand:
	"""The Open sample solutions command is used to read sample solutions."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Open sample solutions"
		self._sample_solutions_caption = "Open sample solutions"
		self._sample_solutions_filter = "*.txt"
		self._sample_solutions_error_bad_input_title = (
			"Sample solutions problem"
		)
		self._sample_solutions_error_bad_input_message = (
			"Input is inconsistent with a sample solutions file.\nLook at "
			"the contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._sample_solutions_caption, self._sample_solutions_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Open sample solutions", "active", params
		)

		# Error handling
		# If not a sample solutions file, then return an error message
		try:
			common.read_sample_solutions_file_check_for_errors(
				file_name, self._director.uncertainty_active
			)
		except ValueError as e:
			raise SpacesError(
				self._sample_solutions_error_bad_input_title,
				self._sample_solutions_error_bad_input_message,
			) from e

		self._director.uncertainty_active.print_sample_solutions()
		self._director.title_for_table_widget = (
			"Sample solutions have been read"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class OpenScoresCommand:
	"""The Open scores command is used to read a scores file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Open scores"
		self._scores_caption = "Open scores"
		self._scores_filter = "*.csv"
		self._scores_error_bad_input_title = "Scores problem"
		self._scores_error_bad_input_message = (
			"Input is inconsistent with a scores file.\nLook at "
			"the contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._scores_caption, self._scores_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Open scores", "active", params
		)

		# Error handling
		# If not a scores file, then return an error message
		try:
			self._read_scores(file_name)
		except ValueError as e:
			raise SpacesError(
				self._scores_error_bad_input_title,
				self._scores_error_bad_input_message,
			) from e

		self._director.scores_active = self._director.scores_candidate
		self._director.scores_original = self._director.scores_active
		self._director.scores_last = self._director.scores_active
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common)
		self._director.scores_active.summarize_scores()
		self._director.scores_active.print_scores()
		self._director.common.create_plot_for_tabs("scores")
		self._director.title_for_table_widget = (
			f"Scores have been read "
			f"({len(self._director.scores_active.scores)} rows)"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_scores(self, file_name: str) -> None:
		"""Read scores from CSV file and store in candidate."""
		try:
			scores = pd.read_csv(file_name)

			if scores.empty:
				raise ValueError("Scores file is empty")

			self._director.scores_candidate.scores = scores
			self._director.scores_candidate.file_handle = file_name

			# Extract dimension names from column headers (skip first column)
			columns = scores.columns.tolist()
			if len(columns) > 1:
				dim_names = columns[1:]  # Skip first column (index column)
				self._director.scores_candidate.dim_names = dim_names

				# Set horizontal and vertical axis names
				if len(dim_names) >= 2:
					self._director.scores_candidate.hor_axis_name = dim_names[0]
					self._director.scores_candidate.vert_axis_name = dim_names[1]
				elif len(dim_names) == 1:
					self._director.scores_candidate.hor_axis_name = dim_names[0]
					self._director.scores_candidate.vert_axis_name = "Dimension 2"

				# Set ndim based on number of score columns
				self._director.scores_candidate.ndim = len(dim_names)

				# Extract score_1 and score_2 for plotting
				if len(dim_names) >= 1:
					hor_axis_name = self._director.scores_candidate.hor_axis_name
					self._director.scores_candidate.score_1 = scores[hor_axis_name]
					self._director.scores_candidate.score_1_name = dim_names[0]

				if len(dim_names) >= 2:
					vert_axis_name = self._director.scores_candidate.vert_axis_name
					self._director.scores_candidate.score_2 = scores[vert_axis_name]
					self._director.scores_candidate.score_2_name = dim_names[1]

		except (
			FileNotFoundError,
			PermissionError,
			pd.errors.EmptyDataError,
			pd.errors.ParserError,
		) as e:
			raise ValueError(f"Unable to read scores file: {e}") from e

	# ------------------------------------------------------------------------


class OpenScriptCommand:
	"""The Open script command is used to read and execute a script file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Open script"
		self._script_caption = "Open script"
		self._script_filter = "*.spc"
		self._script_error_bad_input_title = "Script problem"
		self._script_error_bad_input_message = (
			"Unable to execute script file.\nCheck file format and try again."
		)
		self._executed_commands = []  # Track commands executed in script
		self.index_of_script_in_command_used = None  # Track index for completion
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Save the index of the "Open script" command in the exit code array
		# so we can update it later (after script commands are executed)
		open_script_index = len(self._director.command_exit_code) - 1
		self.index_of_script_in_command_used = open_script_index

		# Default to scripts directory if it exists
		scripts_dir = Path.cwd() / "scripts"
		if scripts_dir.exists():
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._script_caption,
				self._script_filter,
				str(scripts_dir)
			)
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._script_caption, self._script_filter
			)

		# Note: OpenScript doesn't create its own undo state because it
		# executes other commands that will create their own undo states.
		# The individual commands in the script are undoable, not the
		# script execution itself.

		# Read and parse script file
		try:
			with Path(file_name).open("r", encoding="utf-8") as f:
				script_lines = f.readlines()
		except (OSError, UnicodeDecodeError) as e:
			raise SpacesError(
				self._script_error_bad_input_title,
				f"Unable to read script file: {e}",
			) from e

		# Set flag to indicate script execution (no user dialogs)
		self._director.executing_script = True
		commands_executed = 0
		commands_failed = 0

		try:
			# Parse and execute commands
			for line_num, line in enumerate(script_lines, 1):
				line = line.strip()
				# Skip empty lines and comments
				if not line or line.startswith("#"):
					continue

				# Parse command line: command_name param1=value1 param2=value2
				try:
					command_name, params_dict = self._parse_script_line(line)

					# Execute command with parameters
					self._execute_script_command(
						command_name, params_dict, line_num, line
					)
					commands_executed += 1
					self._executed_commands.append(command_name)

				except SpacesError as e:
					# Script command failed - stop execution
					commands_failed += 1
					error_msg = (
						f"Script stopped at line {line_num}: {line}\n"
						f"Error: {e.message}"
					)
					raise SpacesError(
						self._script_error_bad_input_title,
						error_msg,
					) from e

				except Exception as e:  # noqa: BLE001
					# Unexpected error - stop execution
					commands_failed += 1
					error_msg = (
						f"Script stopped at line {line_num}: {line}\n"
						f"Unexpected error: {e}"
					)
					raise SpacesError(
						self._script_error_bad_input_title,
						error_msg,
					) from e

		finally:
			# Always clear script execution flag
			self._director.executing_script = False

		# Reset command name to "Open script" before recording completion
		# (otherwise it will print success message for the last script command)
		self._director.command = "Open script"

		# Set current_command to self so widget_control calls this command's _display
		# (not the last executed command's _display)
		self._director.current_command = self

		# Call _display to create the widget showing executed commands
		self._display()
		self._director.title_for_table_widget = (
			f"Script executed: {commands_executed} commands from "
			f"{Path(file_name).name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")

		# Update the "Open script" command's exit code directly
		# (can't use record_command_as_successfully_completed because that
		# would update the last script command's exit code, not Open script's)
		self._director.command_exit_code[open_script_index] = 0
		self._director.spaces_statusbar.showMessage(
			"Completed Open script command", 80000
		)
		print("\nSuccessfully completed Open script command.")
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for script execution completion.

		Returns:
			QTextEdit widget showing script execution summary
		"""
		from PySide6.QtWidgets import QTextEdit  # noqa: PLC0415

		# Create text widget with command list
		widget = QTextEdit()
		widget.setReadOnly(True)

		# Build summary text
		summary_lines = [
			f"Executed {len(self._executed_commands)} commands:\n"
		]

		for idx, cmd_name in enumerate(self._executed_commands, 1):
			summary_lines.append(f"{idx}. {cmd_name}")

		widget.setPlainText("\n".join(summary_lines))
		self._director.output_widget_type = "Table"

		return widget

	# ------------------------------------------------------------------------

	def _parse_script_line(self, line: str) -> tuple[str, dict]:
		"""Parse a script line into command name and parameters.

		Args:
			line: Script line (e.g., "Reference points contest=['Carter', 'Ford']")

		Returns:
			Tuple of (command_name, params_dict)
		"""
		import ast  # noqa: PLC0415
		from dictionaries import command_dict  # noqa: PLC0415

		# Split into tokens, but preserve quoted strings and brackets
		# For now, use simple split - parameters will be parsed separately
		parts = line.split()

		# Find command name (may be multi-word)
		command_name = self._parse_command_name_from_line(parts)

		# Parse parameters
		params_dict = {}
		param_start = len(command_name.split())

		# Rejoin remaining parts to handle values with spaces
		param_str = " ".join(parts[param_start:])

		if param_str:
			# Parse key=value pairs
			# Handle cases like: file_name=path or contest=['a', 'b']
			current_key = None
			current_value = ""
			in_brackets = 0

			i = 0
			while i < len(param_str):
				char = param_str[i]

				if char == "=" and current_key is None and in_brackets == 0:
					# Found key=value separator
					current_key = current_value.strip()
					current_value = ""
				elif char in "[{(" :
					in_brackets += 1
					current_value += char
				elif char in "]})":
					in_brackets -= 1
					current_value += char
				elif char == " " and in_brackets == 0:
					# Space outside brackets - check if we have a complete param
					if current_key and current_value:
						# Try to evaluate Python literals (lists, etc.)
						try:
							params_dict[current_key] = ast.literal_eval(
								current_value.strip()
							)
						except (ValueError, SyntaxError):
							# Not a Python literal, store as string
							# Remove quotes if present
							val = current_value.strip()
							if (
								(val.startswith('"') and val.endswith('"'))
								or (val.startswith("'") and val.endswith("'"))
							):
								val = val[1:-1]
							params_dict[current_key] = val
						current_key = None
						current_value = ""
				else:
					current_value += char

				i += 1

			# Handle last parameter
			if current_key and current_value:
				try:
					params_dict[current_key] = ast.literal_eval(
						current_value.strip()
					)
				except (ValueError, SyntaxError):
					val = current_value.strip()
					if (
						(val.startswith('"') and val.endswith('"'))
						or (val.startswith("'") and val.endswith("'"))
					):
						val = val[1:-1]
					params_dict[current_key] = val

		return command_name, params_dict

	# ------------------------------------------------------------------------

	def _parse_command_name_from_line(self, parts: list[str]) -> str:
		"""Parse command name from line parts by matching against command_dict.

		Finds the longest command name from command_dict that matches
		the beginning of the line. This works for any command length
		without arbitrary word limits.

		Args:
			parts: List of whitespace-separated tokens from script line

		Returns:
			The command name (may be multi-word like "Factor analysis machine learning")
		"""
		from dictionaries import command_dict  # noqa: PLC0415

		line_text = " ".join(parts)

		# Find all commands that match the beginning of the line
		matching_commands = [
			cmd for cmd in command_dict.keys()
			if line_text.startswith(cmd + " ") or line_text == cmd
		]

		# Return the longest match (most specific)
		if matching_commands:
			return max(matching_commands, key=len)

		# No match found
		return parts[0] if parts else ""

	# ------------------------------------------------------------------------

	def _execute_script_command(
		self,
		command_name: str,
		params_dict: dict,
		line_num: int,
		line: str,
	) -> None:
		"""Execute a command from a script with given parameters.

		Args:
			command_name: Name of command to execute
			params_dict: Dictionary of parameters for the command
			line_num: Line number in script (for error messages)
			line: Original line text (for error messages)
		"""
		import inspect  # noqa: PLC0415
		from dictionaries import command_dict  # noqa: PLC0415

		# Get command class from widget_dict (which maps command names to classes)
		widget_dict = self._director.widget_dict

		if command_name not in widget_dict:
			raise SpacesError(
				"Unknown command",
				f"Command '{command_name}' not found in line {line_num}",
			)

		# Skip interactive_only commands (they cannot be scripted)
		if command_name in command_dict:
			cmd_type = command_dict[command_name].get("type")
			if cmd_type == "interactive_only":
				return

		# widget_dict format: [CommandClass, sharing_type, display_lambda]
		command_class = widget_dict[command_name][0]

		# Store script parameters in director for command to access
		self._director.script_parameters = params_dict

		try:
			# Instantiate command
			command_instance = command_class(self._director, self.common)

			# Store command instance in director so _display() can be called
			# for table widget creation (needed for "unique" type commands)
			self._director.current_command = command_instance

			# Check execute method signature to determine if extra param needed
			execute_sig = inspect.signature(command_instance.execute)
			params = list(execute_sig.parameters.keys())

			# Most commands have: execute(self, common)
			# Some have: execute(self, common, extra_param)
			# Note: inspect.signature on bound method excludes 'self'
			# so params only contains 'common' and any extra parameters
			# Call appropriately based on signature
			if len(params) > 1:
				# Has extra parameter - try to provide it from script params
				param_name = params[1]
				if param_name in params_dict:
					extra_value = params_dict[param_name]
					command_instance.execute(self.common, extra_value)
				else:
					# No value in script - check if parameter has default
					param_obj = execute_sig.parameters[param_name]
					if param_obj.default != inspect.Parameter.empty:
						# Has default, call without extra param
						command_instance.execute(self.common)
					else:
						# Required but not provided
						raise SpacesError(
							"Missing parameter",
							f"Command '{command_name}' requires parameter '{param_name}' "
							f"but it was not provided in line {line_num}"
						)
			else:
				# Standard execute(self, common) signature
				command_instance.execute(self.common)

		finally:
			# Clear script parameters
			self._director.script_parameters = None

	# ------------------------------------------------------------------------


class PrintConfigurationCommand:
	"""The Print configuration command is used to print configuration."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print configuration"
		self._director.title_for_table_widget = "Active configuration"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.print_the_configuration()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintCorrelationsCommand:
	"""The Print correlations command is used to print correlations."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print correlations"
		self._director.title_for_table_widget = "Active correlations"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.correlations_active.print_the_correlations(
			width=8,
			decimals=3,
			common=self._director.common,
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintEvaluationsCommand:
	"""The Print evaluations command is used to print evaluations."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print evaluations"
		self._director.title_for_table_widget = "Active evaluations"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.evaluations_active.print_evaluations()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintGroupedDataCommand:
	"""The Print grouped data command is used to print grouped data."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print grouped data"
		self._director.title_for_table_widget = "Active grouped data"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.grouped_data_active.print_grouped_data()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintIndividualsCommand:
	"""The Print individuals command is used to print individuals data."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print individuals"
		self._director.title_for_table_widget = "Active individuals"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.individuals_active.print_individuals()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSampleDesignCommand:
	"""The Print sample design command is used to print sample design."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print sample design"
		self._director.title_for_table_widget = "Active sample design"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.uncertainty_active.print_sample_design()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSampleRepetitionsCommand:
	"""The Print sample repetitions command is used to print sample repetitions."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print sample repetitions"
		self._director.title_for_table_widget = "Active sample repetitions"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.uncertainty_active.print_sample_repetitions()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSampleSolutionsCommand:
	"""The Print sample solutions command is used to print sample solutions."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print sample solutions"
		self._director.title_for_table_widget = "Active sample solutions"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# Implementation for printing sample solutions
		# TODO: Add actual implementation
		self._director.title_for_table_widget = "Sample solutions printing not yet implemented"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintScoresCommand:
	"""The Print scores command is used to print scores."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print scores"
		self._director.title_for_table_widget = "Active scores"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSimilaritiesCommand:
	"""The Print similarities command is used to print similarities."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Print similarities"
		self._director.title_for_table_widget = "Active similarities"
		self._width = 8
		self._decimals = 3
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintTargetCommand:
	"""The Print target command is used to print target ."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Print target"
		self._director.title_for_table_widget = "Target configuration"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.target_active.print_target()
		self._director.title_for_table_widget = (
			f"Target configuration has {self._director.target_active.ndim}"
			f" dimensions and {self._director.target_active.npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SaveConfigurationCommand:
	"""The Save configuration command is used to write a copy of the active
	configuration to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director = director
		self._director.command = "Save configuration"
		self._save_conf_caption = "Save active configuration"
		self._save_conf_filter = "*.txt"
		self._director.name_of_file_written_to = ""

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_conf_caption, self._save_conf_filter, directory="data"
		)
		self._director.configuration_active.write_a_configuration_type_file(
			file_name, self._director.configuration_active
		)
		self._director.name_of_file_written_to = file_name
		self._print_active_configuration_confirmation(file_name)
		name_of_file_written_to = self._director.name_of_file_written_to
		self._director.title_for_table_widget = (
			f"The active configuration has been written to: "
			f"\n {name_of_file_written_to}\n"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_active_configuration_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active configuration has been written to:\n"
			f"\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveGroupedDataCommand:
	"""The Save grouped data command is used to write a copy of the active
	grouped data to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Save grouped data"
		self._save_grouped_caption = "Save active grouped data"
		self._save_grouped_filter = "*.txt"
		self._director.name_of_file_written_to = ""

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_grouped_caption, self._save_grouped_filter, directory="data"
		)
		self._director.grouped_data_active.write_a_grouped_data_file(
			file_name, self._director.grouped_data_active
		)
		self._director.name_of_file_written_to = file_name
		self._print_active_grouped_data_confirmation(file_name)
		name_of_file_written_to = self._director.name_of_file_written_to
		self._director.title_for_table_widget = (
			f"The active grouped data has been written to: "
			f"\n {name_of_file_written_to}\n"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_active_grouped_data_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active grouped data has been written to:\n"
			f"\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveCorrelationsCommand:
	"""The Save correlations command is used to write a copy of the active
	correlations to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save correlations"
		self._save_correlations_caption = "Save active correlations"
		self._save_correlations_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_correlations_caption, self._save_correlations_filter, directory="data"
		)
		# Write correlations to CSV
		correlations_df = pd.DataFrame(
			self._director.correlations_active.correlations_as_square
		)
		correlations_df.to_csv(file_name, index=False)
		self._director.name_of_file_written_to = file_name
		self._print_save_correlations_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active correlations have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_correlations_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active correlations have been written to:\n"
			f"\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveIndividualsCommand:
	"""The Save individuals command is used to write a copy of the active
	individuals to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save individuals"
		self._save_individuals_title = "The response is empty."
		self._save_individuals_message = (
			"A file name is needed to save individuals."
		)
		self._save_individuals_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_individuals_title, self._save_individuals_filter, directory="data"
		)
		self._director.individuals_active.ind_vars.to_csv(file_name)
		self._director.name_of_file_written_to = file_name
		self._print_save_individuals_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active individuals have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_individuals_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active individuals have been written to:\n"
			f"\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveSampleDesignCommand:
	"""The Save sample design command is used to write a copy of the active
	sample design to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save sample design"
		self._save_sample_design_caption = "Save active sample design"
		self._save_sample_design_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_sample_design_caption, self._save_sample_design_filter, directory="data"
		)
		self._write_sample_design_file(file_name)
		self._director.name_of_file_written_to = file_name
		self._print_save_sample_design_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active sample design has been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_sample_design_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active sample design has been written to:\n"
			f"\t{file_name}\n"
		)
		return

	# ------------------------------------------------------------------------

	def _write_sample_design_file(self, file_name: str) -> None:
		uncertainty_active = self._director.uncertainty_active

		ndim = uncertainty_active.ndim
		npoint = uncertainty_active.npoint
		nfacets = uncertainty_active.nfacets

		with Path(file_name).open("w", encoding="utf-8") as f:
			# Line 1: Comment line
			f.write(
				f"# Sample design file created: "
				f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
			)

			# Line 2: Basic dimensions (I4 format)
			f.write(f"{ndim:4d}{npoint:4d}{nfacets:4d}\n")

			# Section: Description of dimensions
			for i in range(ndim):
				dim_label = uncertainty_active.dim_labels[i]
				dim_name = uncertainty_active.dim_names[i]
				f.write(f"{dim_label};{dim_name}\n")

			# Section: Description of points
			for i in range(npoint):
				point_label = uncertainty_active.point_labels[i]
				point_name = uncertainty_active.point_names[i]
				f.write(f"{point_label};{point_name}\n")

			# Section: Description of facets
			for i in range(nfacets):
				facet_label = uncertainty_active.facet_labels[i]
				facet_name = uncertainty_active.facet_names[i]
				f.write(f"{facet_label};{facet_name}\n")

			# Section: Sample design data
			design_df = uncertainty_active.sample_design_df
			for row_idx in range(len(design_df)):
				for col_idx in range(len(design_df.columns)):
					value = design_df.iloc[row_idx, col_idx]
					f.write(f"{value:8.4f}")
				f.write("\n")


# ----------------------------------------------------------------------------


class SaveSampleRepetitionsCommand:
	"""The Save sample repetitions command is used to write a copy of the active
	sample repetitions to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save sample repetitions"
		self._save_sample_repetitions_caption = (
			"Save active sample repetitions"
		)
		self._save_sample_repetitions_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_sample_repetitions_caption,
			self._save_sample_repetitions_filter,
			directory="data"
		)
		self._write_sample_repetitions_file(file_name)
		self._director.name_of_file_written_to = file_name
		self._print_save_sample_repetitions_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active sample repetitions have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_sample_repetitions_confirmation(
		self, file_name: str
	) -> None:
		print(
			f"\n\tThe active sample repetitions have been written to:\n"
			f"\t{file_name}\n"
		)
		return

	# ------------------------------------------------------------------------

	def _write_sample_repetitions_file(self, file_name: str) -> None:
		uncertainty_active = self._director.uncertainty_active

		ndim = uncertainty_active.ndim
		npoint = uncertainty_active.npoint
		nrepetitions = uncertainty_active.nrepetitions

		with Path(file_name).open("w", encoding="utf-8") as f:
			# Line 1: Comment line
			f.write(
				f"# Sample repetitions file created: "
				f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
			)

			# Line 2: Basic dimensions (I4 format)
			f.write(f"{ndim:4d}{npoint:4d}{nrepetitions:4d}\n")

			# Section: Description of dimensions
			for i in range(ndim):
				dim_label = uncertainty_active.dim_labels[i]
				dim_name = uncertainty_active.dim_names[i]
				f.write(f"{dim_label};{dim_name}\n")

			# Section: Description of points
			for i in range(npoint):
				point_label = uncertainty_active.point_labels[i]
				point_name = uncertainty_active.point_names[i]
				f.write(f"{point_label};{point_name}\n")

			# Section: Repetitions data
			repetitions_df = uncertainty_active.repetitions_df
			for row_idx in range(len(repetitions_df)):
				for col_idx in range(len(repetitions_df.columns)):
					value = repetitions_df.iloc[row_idx, col_idx]
					f.write(f"{value:8.4f}")
				f.write("\n")


# ----------------------------------------------------------------------------


class SaveSampleSolutionsCommand:
	"""The Save sample solutions command is used to write a copy of the active
	sample solutions to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save sample solutions"
		self._save_sample_solutions_caption = "Save active sample solutions"
		self._save_sample_solutions_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_sample_solutions_caption,
			self._save_sample_solutions_filter,
			directory="data"
		)
		self._write_sample_solutions_file(file_name)
		self._director.name_of_file_written_to = file_name
		self._print_save_sample_solutions_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active sample solutions have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_sample_solutions_confirmation(
		self, file_name: str
	) -> None:
		print(
			f"\n\tThe active sample solutions have been written to:\n"
			f"\t{file_name}\n"
		)
		return

	# ------------------------------------------------------------------------

	def _write_sample_solutions_file(self, file_name: str) -> None:
		uncertainty_active = self._director.uncertainty_active

		ndim = uncertainty_active.ndim
		npoint = uncertainty_active.npoint
		nsolutions = uncertainty_active.nsolutions

		with Path(file_name).open("w", encoding="utf-8") as f:
			# Line 1: Comment line
			f.write(
				f"# Sample solutions file created: "
				f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
			)

			# Line 2: Basic dimensions (I4 format)
			f.write(f"{ndim:4d}{npoint:4d}{nsolutions:4d}\n")

			# Section: Description of dimensions
			for i in range(ndim):
				dim_label = uncertainty_active.dim_labels[i]
				dim_name = uncertainty_active.dim_names[i]
				f.write(f"{dim_label};{dim_name}\n")

			# Section: Description of points
			for i in range(npoint):
				point_label = uncertainty_active.point_labels[i]
				point_name = uncertainty_active.point_names[i]
				f.write(f"{point_label};{point_name}\n")

			# Section: Stress information for each repetition
			stress_df = uncertainty_active.solutions_stress_df
			for i in range(nsolutions):
				repetition = stress_df.iloc[i, 0]  # Repetition number
				stress = stress_df.iloc[i, 1]  # Stress value
				f.write(f"{repetition:4d}{stress:8.4f}\n")

			# Section: Coordinates for all points for all solutions
			# solutions_df has columns for dimension, rows for points*solutions
			for solution_idx in range(nsolutions):
				for point_idx in range(npoint):
					# Calculate the row index in the DataFrame
					row_idx = solution_idx * npoint + point_idx

					# Write coordinates for this point (8.4f format)
					coords = []
					for dim_idx in range(ndim):
						coord_value = solutions_df.iloc[row_idx, dim_idx]
						coords.append(f"{coord_value:8.4f}")
					f.write("".join(coords) + "\n")


# --------------------------------------------------------------------------


class SaveScoresCommand:
	"""The Save scores command is used to write a copy of the active
	scores to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save scores"
		self._save_scores_title = "The response is empty."
		self._save_scores_message = "A file name is needed to save scores."
		self._save_scores_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		return

	# -----------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		score_1_name = self._director.scores_active.score_1_name
		score_2_name = self._director.scores_active.score_2_name

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_scores_title, self._save_scores_filter, directory="data"
		)
		self._director.scores_active.scores.to_csv(
			file_name, columns=[score_1_name, score_2_name]
		)
		self._director.name_of_file_written_to = file_name
		self._print_save_scores_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active scores have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_scores_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active scores have been written to:\n\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveScriptCommand:
	"""The Save script command is used to export command history to a script file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save script"
		self._save_script_caption = "Save command history as script"
		self._save_script_filter = "*.spc"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		file_name = self._director.get_file_name_to_store_file(
			self._save_script_caption,
			self._save_script_filter
		)

		# Get command history from undo stack
		undo_stack = self._director.undo_stack

		# Collect commands with their parameters from undo stack
		script_lines = []
		for i, cmd_state in enumerate(undo_stack):
			# Skip commands with empty names
			if not cmd_state.command_name:
				continue

			# Skip script-type commands (OpenScript, SaveScript, ViewScript)
			# These are meta-commands that should not appear in generated scripts
			if cmd_state.command_type == "script":
				continue

			# Skip interactive_only commands (Create, New grouped data)
			# These require extensive user interaction and cannot be scripted
			if cmd_state.command_type == "interactive_only":
				continue

			# Build command line with parameters
			cmd_line = cmd_state.command_name
			if cmd_state.command_params:
				# Add parameters as key=value pairs
				# Format values appropriately: lists/dicts as-is, strings with quotes if needed
				param_parts = []
				for key, value in cmd_state.command_params.items():
					if isinstance(value, str):
						# String values - add quotes if they contain spaces or special chars
						if ' ' in value or '/' in value or '\\' in value:
							param_parts.append(f'{key}="{value}"')
						else:
							param_parts.append(f'{key}={value}')
					elif isinstance(value, (list, dict)):
						# Lists and dicts - write as Python literals
						param_parts.append(f'{key}={value}')
					else:
						# Numbers, booleans, etc.
						param_parts.append(f'{key}={value}')
				params_str = " ".join(param_parts)
				cmd_line = f"{cmd_line} {params_str}"
			script_lines.append(cmd_line)

		# Write script file
		try:
			with Path(file_name).open("w", encoding="utf-8") as f:
				f.write("# Spaces Script\n")
				f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
				f.write("# Spaces Version: 2025\n")

				for i, line in enumerate(script_lines):
					if i == len(script_lines) - 1:
						f.write(line)
					else:
						f.write(f"{line}\n")

			self._director.name_of_file_written_to = file_name
			self._director.title_for_table_widget = (
				f"Script saved with {len(script_lines)} commands:\n{file_name}"
			)

		except (OSError, UnicodeEncodeError) as e:
			raise SpacesError(
				"Save script failed",
				f"Unable to write script file: {e}",
			) from e

		# Display the script contents
		self._display_saved_script(script_lines, file_name)

		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")

		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display_saved_script(
		self,
		script_lines: list[str],
		file_name: str
	) -> None:
		"""Display the saved script contents to the Output tab."""
		print(f"\nScript saved with {len(script_lines)} commands:")
		print(f"{file_name}\n")
		print("Script contents:")
		for line in script_lines:
			print(f"{line}")
		self._director.title_for_table_widget = f"Saved script: {file_name}"
		return

	# ------------------------------------------------------------------------


class SaveSimilaritiesCommand:
	"""The Save similarities command is used to write a copy of the active
	similarities to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save similarities"
		self._save_similarities_caption = "Save active similarities"
		self._save_similarities_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_similarities_caption, self._save_similarities_filter, directory="data"
		)
		# Write similarities to CSV
		similarities_df = pd.DataFrame(
			self._director.similarities_active.similarities_as_square
		)
		similarities_df.to_csv(file_name, index=False)
		self._director.name_of_file_written_to = file_name
		self._print_save_similarities_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active similarities have been written to:\n {file_name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_similarities_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active similarities have been written to:\n"
			f"\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveTargetCommand:
	"""The Save target command is used to write a copy of the active
	target to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director = director
		self._director.command = "Save target"
		self._save_target_caption = "Save active target"
		self._save_target_filter = "*.txt"
		self._director.name_of_file_written_to = ""

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_target_caption, self._save_target_filter, directory="data"
		)
		self._director.target_active.write_a_configuration_type_file(
			file_name, self._director.target_active
		)
		self._director.name_of_file_written_to = file_name
		self._print_active_target_confirmation(file_name)
		name_of_file_written_to = self._director.name_of_file_written_to
		self._director.title_for_table_widget = (
			f"The active target has been written to: "
			f"\n {name_of_file_written_to}\n"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_active_target_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active target has been written to:\n\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SettingsDisplayCommand:
	"""The Settings display sizing command is used to set display sizing options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - display sizing"
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		axis_extra: float = None,
		displacement: float = None,
		point_size: int = None,
	) -> None:
		from dialogs import ModifyValuesDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Use script parameters
			if "axis_extra" in self._director.script_parameters:
				axis_extra = float(self._director.script_parameters["axis_extra"])
			if "displacement" in self._director.script_parameters:
				displacement = float(self._director.script_parameters["displacement"])
			if "point_size" in self._director.script_parameters:
				point_size = int(self._director.script_parameters["point_size"])

		# If no parameters provided, use dialog
		if axis_extra is None or displacement is None or point_size is None:
			# Get current values as defaults
			current_axis = int(common.axis_extra * 100)
			current_displacement = int(common.displacement * 100)
			current_point = common.point_size

			items = ["Axis extra (%)", "Displacement (%)", "Point size"]
			default_values = [current_axis, current_displacement, current_point]

			dialog = ModifyValuesDialog(
				"Display Sizing Settings",
				items,
				integers=True,
				default_values=default_values,
			)

			if dialog.exec():
				values = dialog.selected_items()
				axis_extra = values[0][1] / 100.0
				displacement = values[1][1] / 100.0
				point_size = values[2][1]
			else:
				raise SpacesError(
					"Settings cancelled",
					"Display sizing settings were not changed",
				)

		# Capture state for undo BEFORE modifications
		params = {
			"axis_extra": axis_extra,
			"displacement": displacement,
			"point_size": point_size,
		}
		self.common.capture_and_push_undo_state(
			"Settings - display sizing", "active", params
		)

		# Apply settings
		common.axis_extra = axis_extra
		common.displacement = displacement
		common.point_size = point_size

		self._director.title_for_table_widget = "Display sizing settings updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsLayoutCommand:
	"""The Settings layout options command is used to set layout options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - layout options"
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		max_cols: int = None,
		width: int = None,
		decimals: int = None,
	) -> None:
		from dialogs import ModifyValuesDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Use script parameters
			if "max_cols" in self._director.script_parameters:
				max_cols = int(self._director.script_parameters["max_cols"])
			if "width" in self._director.script_parameters:
				width = int(self._director.script_parameters["width"])
			if "decimals" in self._director.script_parameters:
				decimals = int(self._director.script_parameters["decimals"])

		# If no parameters provided, use dialog
		if max_cols is None or width is None or decimals is None:
			# Get current values as defaults
			current_max_cols = common.max_cols
			current_width = common.width
			current_decimals = common.decimals

			items = ["Max columns", "Width", "Decimals"]
			default_values = [current_max_cols, current_width, current_decimals]

			dialog = ModifyValuesDialog(
				"Layout Options",
				items,
				integers=True,
				default_values=default_values,
			)

			if dialog.exec():
				values = dialog.selected_items()
				max_cols = values[0][1]
				width = values[1][1]
				decimals = values[2][1]
			else:
				raise SpacesError(
					"Settings cancelled",
					"Layout options were not changed",
				)

		# Capture state for undo BEFORE modifications
		params = {
			"max_cols": max_cols,
			"width": width,
			"decimals": decimals,
		}
		self.common.capture_and_push_undo_state(
			"Settings - layout options", "active", params
		)

		# Apply settings
		common.max_cols = max_cols
		common.width = width
		common.decimals = decimals

		self._director.title_for_table_widget = "Layout options updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsPlaneCommand:
	"""The Settings plane command is used to set the viewing plane."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - plane"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, plane: str = None) -> None:
		from dialogs import ChoseOptionDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "plane" in self._director.script_parameters
		):
			plane = self._director.script_parameters["plane"]

		# Get dimension names from active configuration
		dim_names = self._director.configuration_active.dim_names

		# If no parameter provided, use dialog
		if plane is None:
			title = "Plane Settings"
			items = "Select plane orientation:"
			options = [f"{dim_names[0]} x {dim_names[1]}", f"{dim_names[1]} x {dim_names[0]}"]

			dialog = ChoseOptionDialog(title, items, options)

			if dialog.exec():
				selected_option = dialog.selected_option
				if selected_option == 0:
					plane = f"{dim_names[0]} x {dim_names[1]}"
				elif selected_option == 1:
					plane = f"{dim_names[1]} x {dim_names[0]}"
				else:
					raise SpacesError(
						"Settings cancelled",
						"Plane settings were not changed",
					)
			else:
				raise SpacesError(
					"Settings cancelled",
					"Plane settings were not changed",
				)

		# Parse the plane parameter to determine dimensions
		if plane == f"{dim_names[0]} x {dim_names[1]}":
			hor_axis_name = dim_names[0]
			hor_dim = 0
			vert_axis_name = dim_names[1]
			vert_dim = 1
		elif plane == f"{dim_names[1]} x {dim_names[0]}":
			hor_axis_name = dim_names[1]
			hor_dim = 1
			vert_axis_name = dim_names[0]
			vert_dim = 0
		else:
			raise SpacesError(
				"Invalid plane parameter",
				f"Plane must be '{dim_names[0]} x {dim_names[1]}' or '{dim_names[1]} x {dim_names[0]}'",
			)

		# Capture state for undo BEFORE modifications
		params = {
			"plane": plane,
		}
		self.common.capture_and_push_undo_state(
			"Settings - plane", "active", params
		)

		# Apply settings
		common.hor_dim = hor_dim
		common.vert_dim = vert_dim
		self._director.configuration_active.hor_axis_name = hor_axis_name
		self._director.configuration_active.vert_axis_name = vert_axis_name

		self._director.title_for_table_widget = "Plane settings updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsPlotCommand:
	"""The Settings plot settings command is used to set plot settings."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - plot settings"
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		show_bisector: bool = None,
		show_connector: bool = None,
		show_reference_points: bool = None,
		show_just_reference_points: bool = None,
	) -> None:
		from constants import (  # noqa: PLC0415
			TEST_IF_BISECTOR_SELECTED,
			TEST_IF_CONNECTOR_SELECTED,
			TEST_IF_JUST_REFERENCE_POINTS_SELECTED,
			TEST_IF_REFERENCE_POINTS_SELECTED,
		)
		from dialogs import ModifyItemsDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Use script parameters
			if "show_bisector" in self._director.script_parameters:
				show_bisector = self._director.script_parameters["show_bisector"].lower() == "true"
			if "show_connector" in self._director.script_parameters:
				show_connector = self._director.script_parameters["show_connector"].lower() == "true"
			if "show_reference_points" in self._director.script_parameters:
				show_reference_points = self._director.script_parameters["show_reference_points"].lower() == "true"
			if "show_just_reference_points" in self._director.script_parameters:
				show_just_reference_points = self._director.script_parameters["show_just_reference_points"].lower() == "true"

		# If no parameters provided, use dialog
		if (
			show_bisector is None
			or show_connector is None
			or show_reference_points is None
			or show_just_reference_points is None
		):
			# Get current values as defaults
			items = [
				"Show bisector",
				"Show connector",
				"Show reference points",
				"Show just reference points",
			]
			default_values = [
				common.show_bisector,
				common.show_connector,
				common.show_reference_points,
				common.show_just_reference_points,
			]

			dialog = ModifyItemsDialog(
				"Plot Settings", items, default_values=default_values
			)

			if dialog.exec():
				selected_items = dialog.selected_items()
				features_indexes = [
					j
					for i in range(len(selected_items))
					for j in range(len(items))
					if selected_items[i] == items[j]
				]
				show_bisector = TEST_IF_BISECTOR_SELECTED in features_indexes
				show_connector = TEST_IF_CONNECTOR_SELECTED in features_indexes
				show_reference_points = (
					TEST_IF_REFERENCE_POINTS_SELECTED in features_indexes
				)
				show_just_reference_points = (
					TEST_IF_JUST_REFERENCE_POINTS_SELECTED in features_indexes
				)
			else:
				raise SpacesError(
					"Settings cancelled",
					"Plot settings were not changed",
				)

		# Capture state for undo BEFORE modifications
		params = {
			"show_bisector": show_bisector,
			"show_connector": show_connector,
			"show_reference_points": show_reference_points,
			"show_just_reference_points": show_just_reference_points,
		}
		self.common.capture_and_push_undo_state(
			"Settings - plot settings", "active", params
		)

		# Apply settings
		common.show_bisector = show_bisector
		common.show_connector = show_connector
		common.show_reference_points = show_reference_points
		common.show_just_reference_points = show_just_reference_points

		self._director.title_for_table_widget = "Plot settings updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsPresentationLayerCommand:
	"""The Settings presentation layer command is used to set the presentation layer."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - presentation layer"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, layer: str = None) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "layer" in self._director.script_parameters
		):
			# Use script parameter
			layer = self._director.script_parameters["layer"]
		elif layer is None:
			# No layer provided and not in script - this is an error
			raise SpacesError(
				"Missing layer parameter",
				"Settings - presentation layer requires a layer parameter "
				"(either 'Matplotlib' or 'PyQtGraph')"
			)

		# Validate layer parameter
		if layer not in ["Matplotlib", "PyQtGraph"]:
			raise SpacesError(
				"Invalid layer parameter",
				f"Layer must be 'Matplotlib' or 'PyQtGraph', not '{layer}'"
			)

		# Capture state for undo BEFORE modifications
		params = {"layer": layer}
		self.common.capture_and_push_undo_state(
			"Settings - presentation layer", "active", params
		)

		# Apply presentation layer setting
		self._director.common.presentation_layer = layer

		self._director.title_for_table_widget = (
			f"Presentation layer set to: {layer}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsSegmentCommand:
	"""The Settings segment sizing command is used to set segment sizing options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - segment sizing"
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		battleground_size: float = None,
		core_tolerance: float = None,
	) -> None:
		from dialogs import ModifyValuesDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Use script parameters
			if "battleground_size" in self._director.script_parameters:
				battleground_size = float(self._director.script_parameters["battleground_size"])
			if "core_tolerance" in self._director.script_parameters:
				core_tolerance = float(self._director.script_parameters["core_tolerance"])

		# If no parameters provided, use dialog
		if battleground_size is None or core_tolerance is None:
			# Get current values as defaults (convert to percentage)
			current_battleground = int(common.battleground_size * 100)
			current_core = int(common.core_tolerance * 100)

			items = ["Battleground size (%)", "Core tolerance (%)"]
			default_values = [current_battleground, current_core]

			dialog = ModifyValuesDialog(
				"Segment Sizing Settings",
				items,
				integers=True,
				default_values=default_values,
			)

			if dialog.exec():
				values = dialog.selected_items()
				battleground_size = values[0][1] / 100.0
				core_tolerance = values[1][1] / 100.0
			else:
				raise SpacesError(
					"Settings cancelled",
					"Segment sizing settings were not changed",
				)

		# Capture state for undo BEFORE modifications
		params = {
			"battleground_size": battleground_size,
			"core_tolerance": core_tolerance,
		}
		self.common.capture_and_push_undo_state(
			"Settings - segment sizing", "active", params
		)

		# Apply settings
		common.battleground_size = battleground_size
		common.core_tolerance = core_tolerance

		self._director.title_for_table_widget = "Segment sizing settings updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SettingsVectorSizeCommand:
	"""The Settings vector sizing command is used to set vector sizing options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - vector sizing"
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		vector_head_width: float = None,
		vector_width: float = None,
	) -> None:
		from dialogs import ModifyValuesDialog  # noqa: PLC0415

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Use script parameters
			if "vector_head_width" in self._director.script_parameters:
				vector_head_width = float(self._director.script_parameters["vector_head_width"])
			if "vector_width" in self._director.script_parameters:
				vector_width = float(self._director.script_parameters["vector_width"])

		# If no parameters provided, use dialog
		if vector_head_width is None or vector_width is None:
			# Get current values as defaults
			current_head_width = common.vector_head_width
			current_width = common.vector_width

			items = ["Vector head width", "Vector width"]
			default_values = [current_head_width, current_width]

			dialog = ModifyValuesDialog(
				"Vector Sizing Settings",
				items,
				integers=False,
				default_values=default_values,
			)

			if dialog.exec():
				values = dialog.selected_items()
				vector_head_width = values[0][1]
				vector_width = values[1][1]
			else:
				raise SpacesError(
					"Settings cancelled",
					"Vector sizing settings were not changed",
				)

		# Capture state for undo BEFORE modifications
		params = {
			"vector_head_width": vector_head_width,
			"vector_width": vector_width,
		}
		self.common.capture_and_push_undo_state(
			"Settings - vector sizing", "active", params
		)

		# Apply settings
		common.vector_head_width = vector_head_width
		common.vector_width = vector_width

		self._director.title_for_table_widget = "Vector sizing settings updated"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SimilaritiesCommand:
	"""The Similarities command is used to read a similarities file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Similarities"
		self._similarities_caption = "Open similarities"
		self._similarities_filter = "*.txt"
		self._similarities_error_bad_input_title = "Similarities problem"
		self._similarities_error_bad_input_message = (
			"Input is inconsistent with a similarities file.\nLook at "
			"the contents of file and try again."
		)
		self._similarities_error_title = "Similarities inconsistency"
		self._similarities_error_message = (
			"There are inconsistencies with the similarities file.\n"
			"Please check the file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, value_type: str) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
			# Also check for value_type override in script
			if "value_type" in self._director.script_parameters:
				value_type = self._director.script_parameters["value_type"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._similarities_caption, self._similarities_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name, "value_type": value_type}
		self.common.capture_and_push_undo_state(
			"Similarities", "active", params
		)

		# Read and validate similarities file
		self._director.similarities_candidate = common.read_lower_triangular_matrix(
			file_name,
			value_type,
		)

		# Check for consistency between similarities and active configuration
		self._director.dependency_checker.detect_consistency_issues()

		# Convert similarities into different data structures
		self._director.similarities_candidate.duplicate_similarities(common)
		# inserted missing lines here
		self._director.similarities_candidate.range_similarities = \
			range(len(
				self._director.similarities_candidate.similarities_as_list))
		self._director.similarities_candidate.rank_similarities()
		# end of insertion
		self._director.similarities_active = (
			self._director.similarities_candidate
		)
		self._director.similarities_original = (
			self._director.similarities_active
		)
		self._director.similarities_last = self._director.similarities_active
		width = 8
		decimals = 3
		self._director.similarities_active.print_the_similarities(
			width, decimals, common
		)
		self._director.common.create_plot_for_tabs("heatmap_simi")
		nreferent = self._director.similarities_active.nreferent
		value_type = self._director.similarities_active.value_type
		self._director.title_for_table_widget = (
			f"The {value_type} matrix has {nreferent} items"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class TargetCommand:
	"""The Target command is used to open a target file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Target"
		self._target_caption = "Open target"
		self._target_filter = "*.txt"
		self._target_error_bad_input_title = "Target problem"
		self._target_error_bad_input_message = (
			"Input is inconsistent with a target file.\nLook at the "
			"contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "file_name" in self._director.script_parameters
		):
			file_name = self._director.script_parameters["file_name"]
		else:
			file_name = self._director.get_file_name_and_handle_nonexistent_file_names(
				self._target_caption, self._target_filter
			)

		# Capture state for undo BEFORE modifications
		params = {"file_name": file_name}
		self.common.capture_and_push_undo_state(
			"Target", "active", params
		)

		# Read and validate target file
		self._director.target_candidate = common.read_configuration_type_file(
			file_name, "Target"
		)

		self._director.target_active = self._director.target_candidate
		self._director.target_original = self._director.target_active
		self._director.target_last = self._director.target_active
		self._director.target_active.print_target()
		self._director.common.create_plot_for_tabs("target")
		ndim = self._director.target_candidate.ndim
		npoint = self._director.target_candidate.npoint
		self._director.title_for_table_widget = (
			f"Target configuration has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return
