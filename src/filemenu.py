from __future__ import annotations

# Standard library imports
import sys
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pandas as pd
import peek # noqa: F401
from PySide6.QtWidgets import (
	QApplication,
	QMessageBox,
	QTableWidget,
	QTableWidgetItem,
	QTextEdit,
)

# from features import UncertaintyFeature
from modelmenu import UncertaintyAnalysis

if TYPE_CHECKING:
	from common import Spaces
	from director import Status

from exceptions import SpacesError
from rivalry import Rivalry
from constants import(
	MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
	MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_UNCERTAINTY,
	MINIMUM_NUMBER_OF_ITEMS_IN_EVALUATIONS_FILE,
	MINIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING
)

if __name__ == "__main__":  # pragma: no cover
	print("This module is not designed to run as a script.  "
		f"{Path(__file__).name}")
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
			"again.")
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Configuration")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Configuration", "active", params)
		self._director.configuration_active = \
			common.read_configuration_type_file(
			file_name, "Configuration")
		self._director.dependency_checker.detect_consistency_issues()

		self._director.configuration_active.inter_point_distances()
		common.rank_when_similarities_match_configuration()
		self._director.rivalry = Rivalry(self._director)

		self._director.configuration_active.print_active_function()
		common.create_plot_for_tabs("configuration")
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
			"at the contents of file and try again.")
		self._correlations_error_title = "Correlations inconsistency"
		self._correlations_error_message = (
			"There are inconsistencies "
			"with the correlations file.\n"
			"Please check the file and try again.")
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = \
			common.get_command_parameters("Correlations")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Correlations", "active", params)
		self._read_correlations(file_name, common)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.correlations_active.print_the_correlations(
			width=8, decimals=3, common=common)
		common.create_plot_for_tabs("heatmap_corr")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_correlations(self, file_name: str, common: Spaces) -> None:
		"""Read correlations from lower triangular file and store in active.

		Correlations are stored in a lower triangular matrix format, which is
		different from the rectangular format used for evaluations.
		"""
		try:
			self._director.correlations_active = (
				common.read_lower_triangular_matrix(file_name, "correlations")
			)
			self._director.correlations_active.duplicate_correlations(common)
		except (
			FileNotFoundError,
			PermissionError,
			ValueError,
			SpacesError
		):
			restored = common.event_driven_optional_restoration(
				"correlations"
			)
			# Only raise exception if restoration failed
			# If restored, just return - restoration message already
			# informed user
			if not restored:
				raise SpacesError(
					self._correlations_error_bad_input_title,
					self._correlations_error_bad_input_message
				) from None
			# If restored successfully, just return without error
			return

	# ------------------------------------------------------------------------


class CreateCommand:
	"""The Create command creates a new configuration interactively."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Create"
		self._number_of_points_title = "Specify the number of points"
		self._number_of_points_message = (
			"Enter the number of points in the configuration:")
		self._number_of_dimensions_title = "Specify the number of dimensions"
		self._number_of_dimensions_message = (
			"Enter the number of dimensions in the configuration:")
		self._labels_title = "Specify the labels"
		self._labels_message = "Enter a label for "
		self._names_title = "Specify the names"
		self._names_message = "Enter a name for "
		self._coordinates_title = "Specify the coordinates"
		self._coordinates_message = "Enter coordinates for "
		self._cancel_title = "Create cancelled"
		self._cancel_message = "Configuration creation was cancelled"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		config_info = self._get_configuration_information_from_user()

		params = {"npoint": config_info["npoint"], "ndim": config_info["ndim"]}
		common.capture_and_push_undo_state("Create", "active", params)

		self._create_active_configuration(config_info)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.configuration_active.inter_point_distances()
		common.rank_when_similarities_match_configuration()
		self._director.rivalry = Rivalry(self._director)

		self._director.configuration_active.print_active_function()
		common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_configuration_information_from_user(self) -> dict[str, Any]:

		npoint = self._get_number_of_points()
		ndim = self._get_number_of_dimensions()
		point_labels, point_names = self._get_point_labels_and_names(npoint)
		dim_labels, dim_names = self._get_dimension_labels_and_names(ndim)
		coords_data = self._get_coordinates_for_points(
			npoint, ndim, point_names
		)

		point_coords = pd.DataFrame(
			coords_data, index=point_labels, columns=dim_labels
		)

		return {
			"npoint": npoint,
			"ndim": ndim,
			"point_labels": point_labels,
			"point_names": point_names,
			"dim_labels": dim_labels,
			"dim_names": dim_names,
			"point_coords": point_coords,
		}

	# ------------------------------------------------------------------------

	def _create_active_configuration(
		self, config_info: dict[str, Any]
	) -> None:
		"""Set up the active configuration with all necessary data."""
		ndim = config_info["ndim"]
		npoint = config_info["npoint"]
		dim_names = config_info["dim_names"]

		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.npoint = npoint
		self._director.configuration_active.range_dims = range(ndim)
		self._director.configuration_active.range_points = range(npoint)
		self._director.configuration_active.dim_labels = config_info[
			"dim_labels"
		]
		self._director.configuration_active.dim_names = dim_names
		self._director.configuration_active.point_labels = config_info[
			"point_labels"
		]
		self._director.configuration_active.point_names = config_info[
			"point_names"
		]
		self._director.configuration_active.point_coords = config_info[
			"point_coords"
		]
		# Initialize horizontal and vertical axis names to first two dimensions
		if ndim >= MINIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.configuration_active.hor_axis_name = dim_names[0]
		if ndim >= MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.configuration_active.vert_axis_name = dim_names[1]
		return

	# ------------------------------------------------------------------------

	def _get_number_of_points(self) -> int:
		from dialogs import GetIntegerDialog  # noqa: PLC0415

		npoint_dialog = GetIntegerDialog(
			self._number_of_points_title,
			self._number_of_points_message,
			min_value=2,
			max_value=100,
		)
		if not npoint_dialog.exec():
			self.common.event_driven_automatic_restoration()
			raise SpacesError(self._cancel_title, self._cancel_message)
		return npoint_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_number_of_dimensions(self) -> int:
		from dialogs import GetIntegerDialog  # noqa: PLC0415

		ndim_dialog = GetIntegerDialog(
			self._number_of_dimensions_title,
			self._number_of_dimensions_message,
			min_value=2,
			max_value=10,
		)
		if not ndim_dialog.exec():
			self.common.event_driven_automatic_restoration()
			raise SpacesError(self._cancel_title, self._cancel_message)
		return ndim_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_point_labels_and_names(
		self, npoint: int
	) -> tuple[list[str], list[str]]:
		from dialogs import GetStringDialog  # noqa: PLC0415

		point_labels = []
		point_names = []
		for each_point in range(npoint):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}point {each_point + 1}:",
			)
			if not label_dialog.exec():
				self.common.event_driven_automatic_restoration()
				raise SpacesError(self._cancel_title, self._cancel_message)
			point_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}point {each_point + 1}:",
			)
			if not name_dialog.exec():
				self.common.event_driven_automatic_restoration()
				raise SpacesError(self._cancel_title, self._cancel_message)
			point_names.append(name_dialog.get_value())

		return point_labels, point_names

	# ------------------------------------------------------------------------

	def _get_dimension_labels_and_names(
		self, ndim: int
	) -> tuple[list[str], list[str]]:
		from dialogs import GetStringDialog  # noqa: PLC0415

		dim_labels = []
		dim_names = []
		for each_dim in range(ndim):
			label_dialog = GetStringDialog(
				self._labels_title,
				f"{self._labels_message}dimension {each_dim + 1}:",
			)
			if not label_dialog.exec():
				self.common.event_driven_automatic_restoration()
				raise SpacesError(self._cancel_title, self._cancel_message)
			dim_labels.append(label_dialog.get_value())

			name_dialog = GetStringDialog(
				self._names_title,
				f"{self._names_message}dimension {each_dim + 1}:",
			)
			if not name_dialog.exec():
				self.common.event_driven_automatic_restoration()
				raise SpacesError(self._cancel_title, self._cancel_message)
			dim_names.append(name_dialog.get_value())

		return dim_labels, dim_names

	# ------------------------------------------------------------------------

	def _get_coordinates_for_points(
		self, npoint: int, ndim: int, point_names: list[str]
	) -> list[list[float]]:
		from dialogs import GetCoordinatesDialog  # noqa: PLC0415

		coords_data = []
		for each_point in range(npoint):
			coords_dialog = GetCoordinatesDialog(
				self._coordinates_title,
				f"{self._coordinates_message}{point_names[each_point]}:",
				ndim,
			)
			if not coords_dialog.exec():
				self.common.event_driven_automatic_restoration()
				raise SpacesError(self._cancel_title, self._cancel_message)
			coords = coords_dialog.get_values()
			coords_data.append(coords)

		return coords_data

	# ------------------------------------------------------------------------


class DeactivateCommand:
	"""The Deactivate command is used to clear active features."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Deactivate"
		self._deactivate_items_title = "Select items to deactivate"
		self._deactivate_items_message = \
			"Select one or more items to deactivate:"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		available_items, descriptions = self._build_available_items_list()
		selected_items = self._get_user_selection(
			available_items, descriptions)
		params = {"items": selected_items}
		self._capture_conditional_undo_state(selected_items, params)
		deactivated_list = self._deactivate_selected_items(selected_items)
		self._director.deactivated_items = deactivated_list
		self._director.deactivated_descriptions = descriptions
		self._print_deactivated_features(deactivated_list)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _capture_conditional_undo_state(
		self, selected_items: list[str], params: dict
	) -> None:
		"""Capture state for selected items only."""
		from command_state import CommandState  # noqa: PLC0415
		from datetime import datetime  # noqa: PLC0415

		cmd_state = CommandState("Deactivate", "active", params)
		cmd_state.timestamp = datetime.now().strftime( # noqa: DTZ005
			"%Y-%m-%d %H:%M:%S")

		# Map item names to their capture methods
		item_to_capture = {
			"Configuration": cmd_state.capture_configuration_state,
			"Target": cmd_state.capture_target_state,
			"Scores": cmd_state.capture_scores_state,
			"Similarities": cmd_state.capture_similarities_state,
			"Correlations": cmd_state.capture_correlations_state,
			"Evaluations": cmd_state.capture_evaluations_state,
			"Individuals": cmd_state.capture_individuals_state,
			"Grouped data": cmd_state.capture_grouped_data_state,
		}

		# Capture state only for selected items
		for item in selected_items:
			capture_method = item_to_capture.get(item)
			if capture_method:
				capture_method(self._director)

		# Clear redo stack when a new command executes
		self._director.clear_redo_stack()
		self._director.push_undo_state(cmd_state)
		return

	# ------------------------------------------------------------------------

	def _print_deactivated_features(
		self,
		deactivated_list: list[str]
	) -> None:
		"""Print list of deactivated features."""
		print("\n\tDeactivated\n")
		for item in deactivated_list:
			print(f"\t{item}")
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create table widget showing deactivated features."""
		deactivated_items = self._director.deactivated_items
		deactivated_descriptions = self._director.deactivated_descriptions

		# Create table widget
		gui_output_as_widget = QTableWidget()
		gui_output_as_widget.setRowCount(len(deactivated_items))
		gui_output_as_widget.setColumnCount(2)

		# Set headers
		self._director.set_column_and_row_headers(
			gui_output_as_widget, ["Feature", "Description"], []
		)

		# Populate table
		for row_index, item in enumerate(deactivated_items):
			# Feature name
			item_widget = QTableWidgetItem(item)
			gui_output_as_widget.setItem(row_index, 0, item_widget)

			# Description
			desc = deactivated_descriptions[row_index]
			desc_widget = QTableWidgetItem(desc)
			gui_output_as_widget.setItem(row_index, 1, desc_widget)

		# Set column widths
		gui_output_as_widget.setColumnWidth(0, 150)  # Feature column
		gui_output_as_widget.setColumnWidth(1, 300)  # Description column

		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _build_available_items_list(self) -> tuple[list[str], list[str]]:
		"""Build list of active features with descriptions."""
		available_items = []
		descriptions = []
		self._add_configuration_if_active(available_items, descriptions)
		self._add_correlations_if_active(available_items, descriptions)
		self._add_evaluations_if_active(available_items, descriptions)
		self._add_grouped_data_if_active(available_items, descriptions)
		self._add_individuals_if_active(available_items, descriptions)
		self._add_scores_if_active(available_items, descriptions)
		self._add_similarities_if_active(available_items, descriptions)
		self._add_target_if_active(available_items, descriptions)
		self._validate_items_available(available_items)
		return available_items, descriptions

	# ------------------------------------------------------------------------

	def _add_configuration_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add configuration to available items if active."""
		if self._director.configuration_active.ndim > 0:
			available_items.append("Configuration")
			descriptions.append(
				f"ndim={self._director.configuration_active.ndim}, "
				f"npoint={self._director.configuration_active.npoint}")
		return

	# ------------------------------------------------------------------------

	def _add_correlations_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add correlations to available items if active."""
		if len(self._director.correlations_active.correlations) > 0:
			available_items.append("Correlations")
			descriptions.append(
				f"nvar={self._director.correlations_active.nvar}")
		return

	# ------------------------------------------------------------------------

	def _add_evaluations_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add evaluations to available items if active."""
		if not self._director.evaluations_active.evaluations.empty:
			available_items.append("Evaluations")
			descriptions.append(
				f"rows={len(self._director.evaluations_active.evaluations)}")
		return

	# ------------------------------------------------------------------------

	def _add_grouped_data_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add grouped data to available items if active."""
		if self._director.grouped_data_active.ngroups > 0:
			available_items.append("Grouped data")
			descriptions.append(
				f"ngroups={self._director.grouped_data_active.ngroups}")
		return

	# ------------------------------------------------------------------------

	def _add_individuals_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add individuals to available items if active."""
		if not self._director.individuals_active.ind_vars.empty:
			available_items.append("Individuals")
			descriptions.append(
				f"rows={len(self._director.individuals_active.ind_vars)}")
		return

	# ------------------------------------------------------------------------

	def _add_scores_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add scores to available items if active."""
		if not self._director.scores_active.scores.empty:
			available_items.append("Scores")
			descriptions.append(
				f"rows={len(self._director.scores_active.scores)}")
		return

	# ------------------------------------------------------------------------

	def _add_similarities_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add similarities to available items if active."""
		if len(self._director.similarities_active.similarities) > 0:
			available_items.append("Similarities")
			descriptions.append(
				f"nreferent={self._director.similarities_active.nreferent}")
		return

	# ------------------------------------------------------------------------

	def _add_target_if_active(
		self,
		available_items: list[str],
		descriptions: list[str]
	) -> None:
		"""Add target to available items if active."""
		if self._director.target_active.ndim > 0:
			available_items.append("Target")
			descriptions.append(
				f"ndim={self._director.target_active.ndim}, "
				f"npoint={self._director.target_active.npoint}")
		return

	# ------------------------------------------------------------------------

	def _validate_items_available(self, available_items: list[str]) -> None:
		"""Validate that items are available to deactivate."""
		if len(available_items) == 0:
			selection_title = "Nothing to deactivate"
			selection_message = (
				"There are no active features to deactivate.")
			raise SpacesError(selection_title, selection_message)
		return

	# ------------------------------------------------------------------------

	def _get_user_selection(
		self,
		available_items: list[str],
		descriptions: list[str]  # noqa: ARG002
	) -> list[str]:
		"""Get user selection of items to deactivate."""
		from dialogs import SelectItemsDialog  # noqa: PLC0415

		dialog = SelectItemsDialog(
			self._deactivate_items_title, available_items
		)
		self._validate_dialog_executed(dialog)
		selected_items = dialog.selected_items()
		self._validate_items_selected(selected_items)
		return selected_items

	# ------------------------------------------------------------------------

	def _validate_dialog_executed(
		self,
		dialog: object
	) -> None:
		"""Validate that dialog was not cancelled."""
		if not dialog.exec():
			msg_title = "Deactivate cancelled"
			msg = "Deactivation was cancelled"
			raise SpacesError(msg_title, msg)
		return

	# ------------------------------------------------------------------------

	def _validate_items_selected(self, selected_items: list[str]) -> None:
		"""Validate that items were selected."""
		if len(selected_items) == 0:
			nothing_title = "Nothing selected"
			nothing_message = "No items were selected for deactivation."
			raise SpacesError(nothing_title, nothing_message)
		return

	# ------------------------------------------------------------------------

	def _deactivate_selected_items(
		self,
		selected_items: list[str]
	) -> list[str]:
		"""Deactivate the selected items."""
		deactivation_actions = {
			"Configuration": self._director.abandon_configuration,
			"Correlations": self._director.abandon_correlations,
			"Evaluations": self._director.abandon_evaluations,
			"Grouped data": self._director.abandon_grouped_data,
			"Individuals": self._director.abandon_individual_data,
			"Scores": self._director.abandon_scores,
			"Similarities": self._director.abandon_similarities,
			"Target": self._director.abandon_target,
		}
		deactivated_list = []
		for each_item in selected_items:
			action = deactivation_actions.get(each_item)
			if action:
				action()
				deactivated_list.append(each_item)
		return deactivated_list

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
		common.initiate_command_processes()
		params = common.get_command_parameters("Evaluations")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Evaluations", "active", params)
		self._read_evaluations(file_name)
		self._director.dependency_checker.detect_consistency_issues()
		self._compute_correlations_from_evaluations(common)
		self._director.evaluations_active.print_the_evaluations()
		self._director.evaluations_active.summarize_evaluations()
		common.create_plot_for_tabs("evaluations")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_evaluations(self, file_name: str) -> None:
		# Clear linked correlations if they exist and match current evaluations
		self._clear_linked_correlations_if_needed()

		try:
			# Read CSV with type validation
			evaluations = self.common.read_csv_with_type_check(
				file_name, "EVALUATIONS"
			)
			(nevaluators, nreferent) = evaluations.shape
			nitem = nreferent
			range_items = range(nreferent)
			item_names = evaluations.columns.tolist()
			item_labels = [name[:4] for name in item_names]

			if len(item_names) < MINIMUM_NUMBER_OF_ITEMS_IN_EVALUATIONS_FILE:
				self.common.event_driven_automatic_restoration()
				error_title = "Evaluations file problem"
				error_message = "Evaluations file must have at least 3 items"
				raise SpacesError(error_title, error_message) # noqa: TRY301

			# Create a new EvaluationsFeature object
			# (matching Correlations pattern)
			from features import EvaluationsFeature  # noqa: PLC0415
			self._director.evaluations_active = EvaluationsFeature(
				self._director
			)

			# Now set the attributes on the new object
			self._director.evaluations_active.evaluations = evaluations
			self._director.evaluations_active.nevaluators = nevaluators
			self._director.evaluations_active.nreferent = nreferent
			self._director.evaluations_active.nitem = nitem
			self._director.evaluations_active.range_items = range_items
			self._director.evaluations_active.item_names = item_names
			self._director.evaluations_active.item_labels = item_labels
			self._director.evaluations_active.file_handle = file_name

		except (ValueError, SpacesError) as e:
			# read_csv_with_type_check already handles restoration
			# for SpacesError. Handle restoration for ValueError here.
			if isinstance(e, ValueError):
				self.common.event_driven_optional_restoration("evaluations")
			# Raise exception to stop command execution
			raise SpacesError(
				self._evaluations_error_bad_input_title,
				self._evaluations_error_bad_input_message,
			) from e

	# ------------------------------------------------------------------------

	def _clear_linked_correlations_if_needed(self) -> None:
		"""Clear existing correlations if they match existing evaluations."""
		# Check if both evaluations and correlations already exist
		if (
			self._director.evaluations_active.item_names
			and self._director.correlations_active.item_names
			and self._director.evaluations_active.item_names == \
				self._director.correlations_active.item_names
		):
			# Reinitialize correlations since they're linked to
			# old evaluations
			from features import CorrelationsFeature  # noqa: PLC0415
			self._director.correlations_active = CorrelationsFeature(
				self._director
			)
		return

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
				value = correlations_as_dataframe.iloc[each_row, each_col]
				a_row.append(value)
			correlations.append(a_row)

		self._director.correlations_active.nreferent = nreferent
		self._director.correlations_active.nitem = nreferent
		self._director.correlations_active.item_names = item_names
		self._director.correlations_active.item_labels = item_labels
		self._director.correlations_active.correlations = correlations
		self._director.correlations_active.correlations_as_dataframe = (
			correlations_as_dataframe
		)
		self._director.correlations_active.duplicate_correlations(common)
		self._director.correlations_active.ndyad = len(
			self._director.correlations_active.correlations_as_list
		)
		self._director.correlations_active.n_pairs = len(
			self._director.correlations_active.correlations_as_list
		)
		self._director.correlations_active.range_dyads = range(
			self._director.correlations_active.ndyad
		)


	# ------------------------------------------------------------------------


class ExitCommand:
	"""The Exit command is used to exit the application."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Exit"
		self._exit_confirmation_title = "Exit Spaces"
		self._exit_confirmation_message = (
			"Are you sure you want to exit Spaces?"
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		self._handle_exit_confirmation(common)
		return

	# ------------------------------------------------------------------------

	def _handle_exit_confirmation(self, common: Spaces) -> None:
		"""Show confirmation dialog and handle user's choice.

		When executing from a script, exit immediately without confirmation.
		When executing interactively, show confirmation dialog.
		"""
		# Skip confirmation if executing from script
		if self._director.executing_script:
			params = common.get_command_parameters("Exit")
			common.capture_and_push_undo_state("Exit", "passive", params)
			self._director.record_command_as_successfully_completed()
			sys.exit(0)

		# Show confirmation for interactive use
		reply = QMessageBox.question(
			None,
			self._exit_confirmation_title,
			self._exit_confirmation_message,
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
			QMessageBox.StandardButton.No
		)

		if reply == QMessageBox.StandardButton.Yes:
			# User confirmed - exit the application
			params = common.get_command_parameters("Exit")
			common.capture_and_push_undo_state("Exit", "passive", params)
			self._director.record_command_as_successfully_completed()
			sys.exit(0)
		else:
			# User cancelled - print message and mark as failed
			self._print_exit_cancelled()
			self._director.create_widgets_for_output_and_log_tabs()
			self._director.set_focus_on_tab("Output")
			self._director.unable_to_complete_command_set_status_as_failed()
		return

	# ------------------------------------------------------------------------

	def _print_exit_cancelled(self) -> None:
		"""Print message when exit is cancelled."""
		print("\n\tExit cancelled")
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create and return the table widget for cancelled exit output."""
		table = QTableWidget(1, 1)
		table.setHorizontalHeaderLabels(["Status"])
		table.setVerticalHeaderLabels(["Exit"])
		table.setItem(0, 0, QTableWidgetItem("Cancelled"))
		table.resizeColumnsToContents()
		table.resizeRowsToContents()
		self._director.output_widget_type = "Table"
		return table

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
		common.initiate_command_processes()
		params = common.get_command_parameters("Grouped data")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Grouped data", "active", params)
		self._read_grouped_data(file_name)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.grouped_data_active.print_grouped_data()
		common.create_plot_for_tabs("grouped_data")
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
			f"Line for grouping variable name is empty in file: "
			f"\n{file_handle}"
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
		file_handle = self._director.grouped_data_active.file_handle
		self._read_grouped_data_initialized_variables(file_name, file_handle)
		try:
			with Path(file_name).open() as file_handle:
				self._validate_header(file_handle)
				grouping_var = self._read_grouping_var(file_handle)
				expected_dim, expected_groups = self._read_dimensions(
					file_handle)
				dim_labels, dim_names = self._read_dimension_data(
					file_handle, expected_dim)
				group_labels, group_codes, group_names = (
					self._read_group_data(file_handle, expected_groups))
				group_coords = self._read_group_coordinates(
					file_handle, expected_groups, group_names, dim_labels)
				range_groups = range(expected_groups)
				range_dims = range(expected_dim)
		except FileNotFoundError:
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self.group_data_file_not_found_error_title,
				self.group_data_file_not_found_error_message,
			) from None
		except ValueError as e:
			raise SpacesError(
				self._grouped_data_error_bad_input_title,
				self._grouped_data_error_bad_input_message,
			) from e
		self._store_grouped_data_to_active(
			grouping_var, expected_dim, expected_groups,
			dim_names, dim_labels, group_names, group_labels,
			group_codes, group_coords, range_groups, range_dims)
		return

	# ------------------------------------------------------------------------

	def _validate_header(self, file_handle: object) -> None:
		"""Validate the file header is 'grouped'."""
		header = file_handle.readline()
		if len(header) == 0:
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self.grouped_data_file_not_found_error_title,
				self.grouped_data_file_not_found_error_message,
			) from None
		if header.lower().strip() != "grouped":
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self.grouped_data_file_not_grouped_error_title,
				self.grouped_data_file_not_grouped_error_message,
			) from None
		return

	# ------------------------------------------------------------------------

	def _read_grouping_var(self, file_handle: object) -> str:
		"""Read and validate the grouping variable name."""
		grouping_var = file_handle.readline()
		if len(grouping_var) == 0:
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self.missing_grouping_var_error_title,
				self.missing_grouping_var_error_message,
			) from None
		return grouping_var.strip("\n")

	# ------------------------------------------------------------------------

	def _read_dimensions(self, file_handle: object) -> tuple[int, int]:
		"""Read the number of dimensions and groups."""
		dim = file_handle.readline()
		dim_list = dim.strip("\n").split()
		expected_dim = int(dim_list[0])
		expected_groups = int(dim_list[1])
		return expected_dim, expected_groups

	# ------------------------------------------------------------------------

	def _read_dimension_data(
		self,
		file_handle: object,
		expected_dim: int
	) -> tuple[list[str], list[str]]:
		"""Read dimension labels and names."""
		dim_labels = []
		dim_names = []
		for _ in range(expected_dim):
			dim_label, dim_name = file_handle.readline().split(";")
			dim_labels.append(dim_label)
			dim_names.append(dim_name.strip("\n"))
		return dim_labels, dim_names

	# ------------------------------------------------------------------------

	def _read_group_data(
		self,
		file_handle: object,
		expected_groups: int
	) -> tuple[list[str], list[str], list[str]]:
		"""Read group labels, codes, and names."""
		group_labels = []
		group_codes = []
		group_names = []
		for _ in range(expected_groups):
			group_label, group_code, group_name = (
				file_handle.readline().split(";"))
			group_labels.append(group_label)
			group_codes.append(group_code)
			group_names.append(group_name.strip())
		return group_labels, group_codes, group_names

	# ------------------------------------------------------------------------

	def _read_group_coordinates(
		self,
		file_handle: object,
		expected_groups: int,
		group_names: list[str],
		dim_labels: list[str]
	) -> pd.DataFrame:
		"""Read group coordinates and create DataFrame."""
		coords_data = [
			[float(coord) for coord in file_handle.readline().split()]
			for _ in range(expected_groups)
		]
		return pd.DataFrame(
			coords_data,
			index=group_names,
			columns=dim_labels)

	# ------------------------------------------------------------------------

	def _store_grouped_data_to_active(
		self,
		grouping_var: str,
		expected_dim: int,
		expected_groups: int,
		dim_names: list[str],
		dim_labels: list[str],
		group_names: list[str],
		group_labels: list[str],
		group_codes: list[str],
		group_coords: pd.DataFrame,
		range_groups: range,
		range_dims: range
	) -> None:
		"""Store all grouped data to the active feature."""
		self._director.grouped_data_active.grouping_var = grouping_var
		self._director.grouped_data_active.ndim = expected_dim
		self._director.grouped_data_active.dim_names = dim_names
		self._director.grouped_data_active.dim_labels = dim_labels
		self._director.grouped_data_active.npoint = expected_groups
		self._director.grouped_data_active.ngroups = expected_groups
		self._director.grouped_data_active.range_groups = range_groups
		self._director.grouped_data_active.group_names = group_names
		self._director.grouped_data_active.group_labels = group_labels
		self._director.grouped_data_active.group_codes = group_codes
		self._director.grouped_data_active.group_coords = group_coords
		self._director.grouped_data_active.range_dims = range_dims

		# Initialize horizontal and vertical axis names and dimension indices
		if expected_dim >= MINIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.grouped_data_active.hor_axis_name = dim_names[0]
			self._director.grouped_data_active._hor_dim = dim_names.index(
				self._director.grouped_data_active.hor_axis_name
			)
		if expected_dim >= MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.grouped_data_active.vert_axis_name = dim_names[1]
			self._director.grouped_data_active._vert_dim = dim_names.index(
				self._director.grouped_data_active.vert_axis_name
			)
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

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Individuals")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Individuals", "active", params)
		common.read_individuals_file(
				file_name, self._director.individuals_active)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.individuals_active.print_individuals()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class NewGroupedDataCommand:
	"""The New grouped data command is used to create grouped data."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "New grouped data"
		self._group_title = "Grouping variable"
		self._group_label = "Enter name of grouping variable"
		self._group_default = {"Grouping variable"}
		self._group_max_chars = 32
		self._number_of_groups_title = "Specify the number of groups"
		self._number_of_groups_message = (
			"Enter the number of groups in the grouped data:")
		self._number_of_dimensions_title = "Specify the number of dimensions"
		self._number_of_dimensions_message = (
			"Enter the number of dimensions in the grouped data:")
		self._labels_title = "Specify the labels"
		self._labels_message = "Enter a label for "
		self._names_title = "Specify the names"
		self._names_message = "Enter a name for "
		self._coordinates_title = "Specify the coordinates"
		self._coordinates_message = "Enter coordinates for "
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		self._get_grouping_var()
		ngroups = self._get_number_of_groups()
		ndim = self._get_number_of_dimensions()
		group_labels, group_names, group_codes = (
			self._get_group_labels_and_names(ngroups))
		dim_labels, dim_names = self._get_dimension_labels_and_names(ndim)
		coords_data = self._get_coordinates_for_groups(
			ngroups, ndim, group_names)
		group_coords = pd.DataFrame(
			coords_data, index=group_names, columns=dim_labels)
		params = {"ngroups": ngroups, "ndim": ndim}
		common.capture_and_push_undo_state(
			"New grouped data", "active", params)
		self._store_grouped_data(
			ndim, ngroups, dim_labels, dim_names,
			group_labels, group_names, group_codes, group_coords)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.grouped_data_active.print_grouped_data()
		common.create_plot_for_tabs("grouped_data")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_number_of_groups(self) -> int:
		"""Get number of groups from user via dialog."""
		from dialogs import GetIntegerDialog  # noqa: PLC0415

		ngroups_dialog = GetIntegerDialog(
			self._number_of_groups_title,
			self._number_of_groups_message,
			min_value=2,
			max_value=100,
		)
		self._validate_dialog_executed(ngroups_dialog)
		return ngroups_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_number_of_dimensions(self) -> int:
		"""Get number of dimensions from user via dialog."""
		from dialogs import GetIntegerDialog  # noqa: PLC0415

		ndim_dialog = GetIntegerDialog(
			self._number_of_dimensions_title,
			self._number_of_dimensions_message,
			min_value=2,
			max_value=10,
		)
		self._validate_dialog_executed(ndim_dialog)
		return ndim_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_group_labels_and_names(
		self,
		ngroups: int
	) -> tuple[list[str], list[str], list[str]]:
		"""Get group labels, names, and codes from user via dialogs."""
		group_labels = []
		group_names = []
		group_codes = []
		for each_group in range(ngroups):
			label = self._get_label_for_group(each_group)
			group_labels.append(label)
			name = self._get_name_for_group(each_group)
			group_names.append(name)
			group_codes.append(str(each_group + 1))
		return group_labels, group_names, group_codes

	# ------------------------------------------------------------------------

	def _get_label_for_group(self, group_index: int) -> str:
		"""Get label for a single group from user via dialog."""
		from dialogs import GetStringDialog  # noqa: PLC0415

		label_dialog = GetStringDialog(
			self._labels_title,
			f"{self._labels_message}group {group_index + 1}:",
		)
		self._validate_dialog_executed(label_dialog)
		return label_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_name_for_group(self, group_index: int) -> str:
		"""Get name for a single group from user via dialog."""
		from dialogs import GetStringDialog  # noqa: PLC0415

		name_dialog = GetStringDialog(
			self._names_title,
			f"{self._names_message}group {group_index + 1}:",
		)
		self._validate_dialog_executed(name_dialog)
		return name_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_dimension_labels_and_names(
		self,
		ndim: int
	) -> tuple[list[str], list[str]]:
		"""Get dimension labels and names from user via dialogs."""
		dim_labels = []
		dim_names = []
		for each_dim in range(ndim):
			label = self._get_label_for_dimension(each_dim)
			dim_labels.append(label)
			name = self._get_name_for_dimension(each_dim)
			dim_names.append(name)
		return dim_labels, dim_names

	# ------------------------------------------------------------------------

	def _get_label_for_dimension(self, dim_index: int) -> str:
		"""Get label for a single dimension from user via dialog."""
		from dialogs import GetStringDialog  # noqa: PLC0415

		label_dialog = GetStringDialog(
			self._labels_title,
			f"{self._labels_message}dimension {dim_index + 1}:",
		)
		self._validate_dialog_executed(label_dialog)
		return label_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_name_for_dimension(self, dim_index: int) -> str:
		"""Get name for a single dimension from user via dialog."""
		from dialogs import GetStringDialog  # noqa: PLC0415

		name_dialog = GetStringDialog(
			self._names_title,
			f"{self._names_message}dimension {dim_index + 1}:",
		)
		self._validate_dialog_executed(name_dialog)
		return name_dialog.get_value()

	# ------------------------------------------------------------------------

	def _get_coordinates_for_groups(
		self,
		ngroups: int,
		ndim: int,
		group_names: list[str]
	) -> list[list[float]]:
		"""Get coordinates for each group from user via dialogs."""
		coords_data = []
		for each_group in range(ngroups):
			coords = self._get_coordinates_for_single_group(
				each_group, ndim, group_names)
			coords_data.append(coords)
		return coords_data

	# ------------------------------------------------------------------------

	def _get_coordinates_for_single_group(
		self,
		group_index: int,
		ndim: int,
		group_names: list[str]
	) -> list[float]:
		"""Get coordinates for a single group from user via dialog."""
		from dialogs import GetCoordinatesDialog  # noqa: PLC0415

		coords_dialog = GetCoordinatesDialog(
			self._coordinates_title,
			f"{self._coordinates_message}{group_names[group_index]}:",
			ndim,
		)
		self._validate_dialog_executed(coords_dialog)
		return coords_dialog.get_values()

	# ------------------------------------------------------------------------

	def _validate_dialog_executed(self, dialog: object) -> None:
		"""Validate that dialog was not cancelled."""
		if not dialog.exec():
			self.common.event_driven_automatic_restoration()
			cancelled_title = "Create cancelled"
			cancelled_message = "Grouped data creation was cancelled"
			raise SpacesError(
				cancelled_title, cancelled_message) from None
		return

	# ------------------------------------------------------------------------

	def _store_grouped_data(
		self,
		ndim: int,
		ngroups: int,
		dim_labels: list[str],
		dim_names: list[str],
		group_labels: list[str],
		group_names: list[str],
		group_codes: list[str],
		group_coords: pd.DataFrame
	) -> None:
		"""Store the new grouped data in active feature."""
		self._director.grouped_data_active.ndim = ndim
		self._director.grouped_data_active.ngroups = ngroups
		self._director.grouped_data_active.range_dims = range(ndim)
		self._director.grouped_data_active.range_groups = range(ngroups)
		self._director.grouped_data_active.dim_labels = dim_labels
		self._director.grouped_data_active.dim_names = dim_names
		self._director.grouped_data_active.group_labels = group_labels
		self._director.grouped_data_active.group_names = group_names
		self._director.grouped_data_active.group_codes = group_codes
		self._director.grouped_data_active.group_coords = group_coords
		# Initialize horizontal and vertical axis names and dimension indices
		if ndim >= MINIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.grouped_data_active.hor_axis_name = dim_names[0]
			self._director.grouped_data_active._hor_dim = dim_names.index(
				self._director.grouped_data_active.hor_axis_name
			)
		if ndim >= MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.grouped_data_active.vert_axis_name = dim_names[1]
			self._director.grouped_data_active._vert_dim = dim_names.index(
				self._director.grouped_data_active.vert_axis_name
			)
		return

	# ------------------------------------------------------------------------

	def _get_grouping_var_initialize_variables(self) -> None:
		self.missing_grouping_var_error_title = (
			"New grouped data configuration")
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
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self.missing_grouping_var_error_title,
				self.missing_grouping_var_error_message,
			)

		self._director.grouped_data_active.grouping_var = grouping_var
		return

	# ------------------------------------------------------------------------


class OpenSampleDesignCommand:
	"""The Open sample design command is used to read a sample design file.

	DEPRECATED: This command is deprecated and may be removed in a future
	version. The Uncertainty command now handles sample design internally.
	"""

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
		common.initiate_command_processes()
		params = common.get_command_parameters("Open sample design")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Open sample design", "active", params
		)
		self._read_sample_design_file(common, file_name)
		self._director.uncertainty_active.print_sample_design()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_sample_design_file(
		self, common: Spaces, file_name: str
	) -> None:
		"""Read sample design file with error handling."""
		try:
			common.read_sample_design_file_check_for_errors(
				file_name, self._director.uncertainty_active
			)
		except ValueError as e:
			raise SpacesError(
				self._sample_design_error_bad_input_title,
				self._sample_design_error_bad_input_message,
			) from e

	# ------------------------------------------------------------------------


class OpenSampleRepetitionsCommand:
	"""The Open sample repetitions command reads sample repetitions.

	DEPRECATED: This command is deprecated and may be removed in a future
	version. The Uncertainty command now handles sample repetitions internally.
	"""

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
		common.initiate_command_processes()
		params = common.get_command_parameters("Open sample repetitions")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Open sample repetitions", "active", params
		)
		self._read_sample_repetitions_file(common, file_name)
		self._director.uncertainty_active.print_sample_repetitions()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_sample_repetitions_file(
		self, common: Spaces, file_name: str
	) -> None:
		"""Read sample repetitions file with error handling."""
		try:
			common.read_sample_repetitions_file_check_for_errors(
				file_name, self._director.uncertainty_active
			)
		except ValueError as e:
			raise SpacesError(
				self._sample_repetitions_error_bad_input_title,
				self._sample_repetitions_error_bad_input_message,
			) from e

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
			"Sample solutions problem")
		self._sample_solutions_error_bad_input_message = (
			"Input is inconsistent with a sample solutions file.\nLook at "
			"the contents of file and try again.")
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Open sample solutions")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Open sample solutions", "active", params
		)
		self._read_sample_solutions_file_check_for_errors(file_name)
		self._director.uncertainty_active.print_sample_solutions()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_sample_solutions_file_check_for_errors(
		self, file_name: str
	) -> None:
		"""Read sample solutions file and validate format."""
		try:

			with Path(file_name).open("r", encoding="utf-8") as f:
				# Line 1: Comment line (skip)
				f.readline()

				# Line 2: ndim, npoint, nsolutions (4-character integers)
				dimensions_line = f.readline().strip()
				if len(dimensions_line) < \
					MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_UNCERTAINTY:
					invalid_format_title = "Sample solutions format issue"
					invalid_format_message = "Invalid dimensions line format"
					raise SpacesError(
						invalid_format_title, invalid_format_message)

				ndim = int(dimensions_line[0:4])
				npoint = int(dimensions_line[4:8])
				nsolutions = int(dimensions_line[8:12])

				# Read dimension labels and names
				dim_labels = []
				dim_names = []
				for _ in range(ndim):
					line = f.readline().strip()
					if ";" not in line:
						no_semicolon_title = "Sample solutions format issue"
						no_semicolon_message = "Invalid dimension format"
						raise SpacesError(
							no_semicolon_title, no_semicolon_message)
					label, name = line.split(";", 1)
					dim_labels.append(label)
					dim_names.append(name)

				# Read point labels and names
				point_labels = []
				point_names = []
				for _ in range(npoint):
					line = f.readline().strip()
					if ";" not in line:
						invalid_point_title = "Sample solutions format issue"
						invalid_point_message = "Invalid point format"
						raise SpacesError(
							invalid_point_title,
							invalid_point_message)
					label, name = line.split(";", 1)
					point_labels.append(label)
					point_names.append(name)

				# Create new UncertaintyFeature object
				#self._director.uncertainty_active = UncertaintyFeature(
				self._director.uncertainty_active = UncertaintyAnalysis(
					self._director
				)

				# Store basic dimensions
				self._director.uncertainty_active.ndim = ndim
				self._director.uncertainty_active.npoint = npoint
				self._director.uncertainty_active.nsolutions = nsolutions
				self._director.uncertainty_active.dim_labels = dim_labels
				self._director.uncertainty_active.dim_names = dim_names
				self._director.uncertainty_active.point_labels = point_labels
				self._director.uncertainty_active.point_names = point_names

				# Read stress data and solution coordinates
				# This is a shell implementation - full reading
				# not yet complete

		except (FileNotFoundError, ValueError, IndexError) as e:
			self.common.event_driven_automatic_restoration()
			raise SpacesError(
				self._sample_solutions_error_bad_input_title,
				self._sample_solutions_error_bad_input_message,
			) from e

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
		common.initiate_command_processes()
		params = common.get_command_parameters("Open scores")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Open scores", "active", params)

		self._read_scores(file_name)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common)
		self._director.scores_active.summarize_scores()
		self._director.scores_active.print_scores()
		common.create_plot_for_tabs("scores")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_scores(self, file_name: str) -> None:
		"""Read scores from CSV file and store in active."""
		try:
			# Read CSV with type validation
			scores = self.common.read_csv_with_type_check(file_name, "SCORES")

			if scores.empty:
				self.common.event_driven_automatic_restoration()
				empty_file_title = "Empty scores file"
				empty_file_message = "Scores file is empty"
				raise SpacesError(
					empty_file_title,
					empty_file_message)

			# Create a new ScoresFeature object (matching Evaluations pattern)
			from features import ScoresFeature  # noqa: PLC0415
			self._director.scores_active = ScoresFeature(self._director)

			# Now set the attributes on the new object
			self._director.scores_active.scores = scores
			self._director.scores_active.file_handle = file_name
			self._director.scores_active.nscores = scores.shape[1] - 1
			self._director.scores_active.nscored_individ = scores.shape[0]
			self._director.scores_active.n_individ = (
				self._director.scores_active.nscored_individ
			)
			self._director.scores_active.range_scores = range(
				self._director.scores_active.nscores
			)

			# Extract dimension names from column headers (skip first column)
			columns = scores.columns.tolist()
			if len(columns) > 1:
				dim_names = columns[1:]  # Skip first column (index column)
				self._director.scores_active.dim_names = dim_names

				# Set horizontal and vertical axis names
				if len(dim_names) >= \
					MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
					self._director.scores_active.hor_axis_name = dim_names[0]
					self._director.scores_active.vert_axis_name = dim_names[1]
				elif len(dim_names) == 1:
					self._director.scores_active.hor_axis_name = dim_names[0]
					self._director.scores_active.vert_axis_name = "Dimension 2"
					self._director.scores_active._hor_dim = dim_names.index(
						self._director.scores_active.hor_axis_name
					)
					self._director.scores_active._vert_dim = dim_names.index(
						self._director.scores_active.vert_axis_name
					)

				# Set ndim based on number of score columns
				self._director.scores_active.ndim = len(dim_names)

				# Extract score_1 and score_2 for plotting
				if len(dim_names) >= MINIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
					hor_axis_name = (
						self._director.scores_active.hor_axis_name)
					self._director.scores_active.score_1 = (
						scores[hor_axis_name])
					self._director.scores_active.score_1_name = dim_names[0]
					self._director.scores_active._hor_dim = dim_names.index(
						self._director.scores_active.hor_axis_name
					)

				if len(dim_names) >= MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
					vert_axis_name = (
						self._director.scores_active.vert_axis_name)
					self._director.scores_active.score_2 = (
						scores[vert_axis_name])
					self._director.scores_active.score_2_name = dim_names[1]
					self._director.scores_active._vert_dim = dim_names.index(
						self._director.scores_active.vert_axis_name
					)

		except (ValueError, SpacesError) as e:
			# read_csv_with_type_check already handles restoration
			# for SpacesError. Handle restoration for ValueError here.
			if isinstance(e, ValueError):
				self.common.event_driven_optional_restoration("scores")
			# Raise exception to stop command execution
			raise SpacesError(
				self._scores_error_bad_input_title,
				self._scores_error_bad_input_message,
			) from e

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
		self._executed_commands = []  # Track executed commands
		self.index_of_script_in_command_used = None  # Track index
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()

		# Save the index of the "Open script" command in the exit code array
		# so we can update it later (after script commands are executed)
		open_script_index = len(self._director.command_exit_code) - 1
		self.index_of_script_in_command_used = open_script_index

		# Note: OpenScript doesn't create its own undo state because it
		# executes other commands that will create their own undo states.
		# The individual commands in the script are undoable, not the
		# script execution itself.

		# Get file name and read script lines
		file_name, script_lines = self._read_script_file()

		# Execute the script
		commands_executed = self._execute_script_lines(script_lines)

		# Reset command name to "Open script" after script execution
		# (otherwise it will print success message for the last script command)
		self._director.command = "Open script"

		# Set current_command to self so widget_control calls
		# this command's _display (not the last executed command's _display)
		self._director.current_command = self

		# Call _display to create the widget showing executed commands
		self._display()

		# Store values for title generation
		common.commands_executed = commands_executed
		common.script_file_name = Path(file_name).name

		# Standard completion steps
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")

		# Update the "Open script" command's exit code directly
		# Must set the specific index because the command stack has grown
		# during script execution
		self._director.command_exit_code[open_script_index] = 0

		# Standard completion (provides success message)
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_script_file(self) -> tuple[str, list[str]]:
		"""Get script file name and read its contents.

		Returns:
			Tuple of (file_name, script_lines)
		"""
		# Default to scripts directory if it exists
		scripts_dir = Path.cwd() / "scripts"
		if scripts_dir.exists():
			file_name = (
				self._director.get_file_name_and_handle_nonexistent_file_names(
					self._script_caption,
					self._script_filter,
					str(scripts_dir)
				))
		else:
			file_name = (
				self._director.get_file_name_and_handle_nonexistent_file_names(
					self._script_caption, self._script_filter
				))

		# Read script file
		try:
			with Path(file_name).open("r", encoding="utf-8") as f:
				script_lines = f.readlines()
		except (OSError, UnicodeDecodeError) as e:
			raise SpacesError(
				self._script_error_bad_input_title,
				f"Unable to read script file: {e}",
			) from e

		return file_name, script_lines

	# ------------------------------------------------------------------------

	def _execute_script_lines(self, script_lines: list[str]) -> int:
		"""Execute all commands in the script.

		Args:
			script_lines: Lines from the script file

		Returns:
			Number of commands executed
		"""
		# Set flag to indicate script execution (no user dialogs)
		self._director.executing_script = True
		commands_executed = 0

		# Count total executable lines (non-empty, non-comment)
		total_commands = sum(
			1 for line in script_lines
			if line.strip() and not line.strip().startswith("#")
		)

		# Setup progress bar
		director = self._director
		director.progress_bar.setRange(0, total_commands)
		director.progress_bar.setValue(0)
		director.progress_bar.setStyleSheet("")
		director.progress_label.setText(
			f"Executing line 0 of {total_commands}"
		)
		director.progress_label.show()
		director.progress_spacer.show()
		director.progress_bar.show()

		try:
			# Parse and execute commands
			for line_num, line in enumerate(script_lines, 1):
				line = line.strip() # noqa: PLW2901
				# Skip empty lines and comments
				if not line or line.startswith("#"):
					continue

				# Parse and execute command line
				try:
					command_name, params_dict = (
						self.common.parse_script_line(line))

					# Execute command with parameters
					self._execute_script_command(
						command_name, params_dict, line_num
					)
					commands_executed += 1
					self._executed_commands.append(command_name)

					# Update progress bar
					director.progress_bar.setValue(commands_executed)
					director.progress_label.setText(
						f"Executing line {commands_executed} of "
						f"{total_commands}"
					)
					QApplication.processEvents()

				except SpacesError as e:
					# Script command failed - stop execution
					error_msg = (
						f"Script stopped at line {line_num}: {line}\n"
						f"Error: {e.message}"
					)
					raise SpacesError(
						self._script_error_bad_input_title,
						error_msg,
					) from e

				except Exception as e:
					# Unexpected error - stop execution
					error_msg = (
						f"Script stopped at line {line_num}: {line}\n"
						f"Unexpected error: {e}"
					)
					raise SpacesError(
						self._script_error_bad_input_title,
						error_msg,
					) from e

		finally:
			# Always clear script execution flag and hide progress bar
			self._director.executing_script = False
			director.progress_bar.hide()
			director.progress_label.hide()
			director.progress_spacer.hide()

		return commands_executed

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for script execution completion.

		Returns:
			QTextEdit widget showing script execution summary
		"""
		from PySide6.QtWidgets import QTextEdit  # noqa: PLC0415
		from PySide6.QtGui import QFontMetrics  # noqa: PLC0415

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

		# Calculate and set fixed height based on content
		# This prevents scrolling in the log tab
		font_metrics = QFontMetrics(widget.font())
		line_height = font_metrics.lineSpacing()
		num_lines = len(summary_lines)
		content_height = num_lines * line_height
		# Add padding for margins and frame
		total_height = content_height + 40
		widget.setFixedHeight(total_height)

		self._director.output_widget_type = "Table"

		return widget

	# ------------------------------------------------------------------------

	def _execute_script_command(
		self,
		command_name: str,
		params_dict: dict,
		line_num: int
	) -> None:
		"""Execute a command from a script with given parameters.

		Args:
			command_name: Name of command to execute
			params_dict: Dictionary of parameters for the command
			line_num: Line number in script (for error messages)
		"""
		import inspect  # noqa: PLC0415
		from dictionaries import command_dict  # noqa: PLC0415

		# Get command class from widget_dict
		# (which maps command names to classes)
		widget_dict = self._director.widget_dict

		if command_name not in widget_dict:
			unknown_command_title = "Unknown command"
			unknown_command_message = \
				f"Command '{command_name}' not found in line {line_num}"
			raise SpacesError(unknown_command_title, unknown_command_message)

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
						missing_param_title = "Missing parameter"
						missing_param_message = (
							f"Command '{command_name}' requires "
							f"parameter '{param_name}' but it was not "
							f"provided in line {line_num}"
						)
						raise SpacesError(missing_param_title,
						missing_param_message)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print configuration")
		common.capture_and_push_undo_state(
			"Print configuration", "passive", params)
		
		# Use capture_and_print to redirect output to printer
		common.capture_and_print(self._director.print_the_configuration)
		
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print correlations")
		common.capture_and_push_undo_state(
			"Print correlations", "passive", params)
		common.capture_and_print(
			lambda: self._director.correlations_active.print_the_correlations(
				width=8, decimals=3, common=common
			)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print evaluations")
		common.capture_and_push_undo_state(
			"Print evaluations", "passive", params)
		common.capture_and_print(
			self._director.evaluations_active.print_the_evaluations)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print grouped data")
		common.capture_and_push_undo_state(
			"Print grouped data", "passive", params)
		common.capture_and_print(
			self._director.grouped_data_active.print_grouped_data)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print individuals")
		common.capture_and_push_undo_state(
			"Print individuals", "passive", params)
		common.capture_and_print(
			self._director.individuals_active.print_individuals)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print sample design")
		common.capture_and_push_undo_state(
			"Print sample design", "passive", params)
		common.capture_and_print(
			self._director.uncertainty_active.print_sample_design)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSampleRepetitionsCommand:
	"""The Print sample repetitions command prints repetitions."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print sample repetitions"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print sample repetitions")
		common.capture_and_push_undo_state(
			"Print sample repetitions", "passive", params)
		common.capture_and_print(
			self._director.uncertainty_active.print_sample_repetitions)
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print sample solutions")
		common.capture_and_push_undo_state(
			"Print sample solutions", "passive", params)
		# Implementation for printing sample solutions
		#  Add actual implementation
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
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print scores")
		common.capture_and_push_undo_state(
			"Print scores", "passive", params)
		common.capture_and_print(
			self._director.scores_active.print_scores)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSimilaritiesCommand:
	"""The Print similarities command is used to print similarities."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print similarities"
		self._width = 8
		self._decimals = 3
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print similarities")
		common.capture_and_push_undo_state(
			"Print similarities", "passive", params
		)
		common.capture_and_print(
			lambda: self._director.similarities_active.print_the_similarities(
				self._width, self._decimals, common
			)
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintTargetCommand:
	"""The Print target command is used to print target ."""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Print target"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Print target")
		common.capture_and_push_undo_state("Print target", "passive", params)
		common.capture_and_print(
			self._director.target_active.print_target)
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
		self._director = director
		self._director.command = "Save configuration"
		self._save_conf_caption = "Save active configuration"
		self._save_conf_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		self._save_conf_error_title = "Configuration save problem"
		self._save_conf_error_message = (
			"Unable to write configuration file.\n"
			"Check file path and permissions, then try again.")

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save configuration")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save configuration", "passive", params)
		self._write_configuration_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_active_configuration_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_configuration_file(self, file_name: str) -> None:
		"""Write configuration to file with error handling."""
		try:
			self._director.common.write_configuration_type_file(
				file_name, self._director.configuration_active)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_conf_error_title,
				self._save_conf_error_message,
			) from e

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
		self._save_grouped_error_title = "Grouped data save problem"
		self._save_grouped_error_message = (
			"Unable to write grouped data file.\n"
			"Check file path and permissions, then try again."
		)

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save grouped data")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save grouped data", "passive", params)
		self._write_grouped_data_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_active_grouped_data_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_grouped_data_file(self, file_name: str) -> None:
		"""Write grouped data to file with error handling."""
		try:
			self._director.grouped_data_active.write_a_grouped_data_file(
				file_name, self._director.grouped_data_active
			)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_grouped_error_title,
				self._save_grouped_error_message,
			) from e

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

	def __init__(self, director: Status, common: Spaces) -> None: # noqa: ARG002
		self._director = director
		self._director.command = "Save correlations"
		self._save_correlations_caption = "Save active correlations"
		self._save_correlations_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		self._save_correlations_error_title = "Correlations save problem"
		self._save_correlations_error_message = (
			"Unable to write correlations file.\n"
			"Check file path and permissions, then try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save correlations")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save correlations", "passive", params)
		self._write_correlations_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_correlations_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_correlations_file(self, file_name: str) -> None:
		"""Write correlations to lower triangular file with error handling."""
		try:
			self.common.write_lower_triangle(
				file_name,
				self._director.correlations_active.correlations_as_list,
				self._director.correlations_active.nitem,
				self._director.correlations_active.item_labels,
				self._director.correlations_active.item_names,
				8,
				5,
			)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_correlations_error_title,
				self._save_correlations_error_message,
			) from e

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

	def __init__(self, director: Status, common: Spaces) -> None: # noqa: ARG002
		self._director = director
		self._director.command = "Save individuals"
		self._save_individuals_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		self._save_individuals_error_title = "Individuals save problem"
		self._save_individuals_error_message = (
			"Unable to write individuals file.\n"
			"Check file path and permissions, then try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save individuals")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save individuals", "passive", params)
		self._write_individuals_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_individuals_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_individuals_file(self, file_name: str) -> None:
		"""Write individuals to CSV file with error handling."""
		try:
			self.common.write_csv_with_type_header(
				self._director.individuals_active.ind_vars,
				file_name,
				"INDIVIDUALS",
				index=False
			)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_individuals_error_title,
				self._save_individuals_error_message,
			) from e

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

	DEPRECATED: This command is deprecated and may be removed in a future
	version. The Uncertainty command now handles sample design internally.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Save sample design"
		self._save_sample_design_caption = "Save active sample design"
		self._save_sample_design_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save sample design")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save sample design", "passive", params
		)
		self._write_sample_design_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_sample_design_confirmation(file_name)
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
		# nfacets = uncertainty_active.nfacets

		with Path(file_name).open("w", encoding="utf-8") as f:
			# Line 1: Comment line
			f.write("# Sample design file created: ")

			# Line 2: Basic dimensions (I4 format)
			# f.write(f"{ndim:4d}{npoint:4d}{nfacets:4d}\n")
			f.write(f"{ndim:4d}{npoint:4d}\n")
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
			# for i in range(nfacets):
			# 	facet_label = uncertainty_active.facet_labels[i]
			# 	facet_name = uncertainty_active.facet_names[i]
			# 	f.write(f"{facet_label};{facet_name}\n")

			# Section: Sample design data
			# design_df = uncertainty_active.sample_design_df
			design_df = uncertainty_active.sample_design

			for row_idx in range(len(design_df)):
				for col_idx in range(len(design_df.columns)):
					value = design_df.iloc[row_idx, col_idx]
					f.write(f"{value:8.4f}")
				f.write("\n")

# ----------------------------------------------------------------------------


class SaveSampleRepetitionsCommand:
	"""The Save sample repetitions command writes active repetitions
	to a file.

	DEPRECATED: This command is deprecated and may be removed in a future
	version. The Uncertainty command now handles sample repetitions internally.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Save sample repetitions"
		self._save_sample_repetitions_caption = (
			"Save active sample repetitions"
		)
		self._save_sample_repetitions_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save sample repetitions")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save sample repetitions", "passive", params
		)
		self._write_sample_repetitions_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_sample_repetitions_confirmation(file_name)
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
		repetitions_df = uncertainty_active.sample_repetitions


		with Path(file_name).open("w", encoding="utf-8") as f:
			# Line 1: Comment line
			f.write(
				f"# Sample repetitions file created: "
				f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" # noqa: DTZ005
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
			# repetitions_df = uncertainty_active.repetitions_df
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

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Save sample solutions"
		self._save_sample_solutions_caption = "Save active sample solutions"
		self._save_sample_solutions_filter = "*.txt"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save sample solutions")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save sample solutions", "passive", params)
		self._write_sample_solutions_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_sample_solutions_confirmation(file_name)
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
			f.write("# Sample solutions file created: ")

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
			solutions_df = uncertainty_active.sample_solutions
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
		self._director = director
		self.common = common
		self._director.command = "Save scores"
		self._save_scores_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		self._save_scores_error_title = "Scores save problem"
		self._save_scores_error_message = (
			"Unable to write scores file.\n"
			"Check file path and permissions, then try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save scores")
		file_name: str = params["file"]
		common.capture_and_push_undo_state("Save scores", "passive", params)
		self._write_scores_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_scores_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_scores_file(self, file_name: str) -> None:
		"""Write scores to CSV file with error handling."""
		try:
			self.common.write_csv_with_type_header(
				self._director.scores_active.scores,
				file_name,
				"SCORES",
				index=False
			)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_scores_error_title,
				self._save_scores_error_message,
			) from e

	# ------------------------------------------------------------------------

	def _print_save_scores_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active scores have been written to:\n\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SaveScriptCommand:
	"""The Save script command exports command history to file."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save script"
		self._save_script_caption = "Save command history as script"
		self._save_script_filter = "*.spc"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save script")
		file_name: str = params["file"]
		common.capture_and_push_undo_state("Save script", "script", params)
		# file_name = self._director.get_file_name_to_store_file(
		# 	self._save_script_caption,
		# 	self._save_script_filter)
		script_lines = self._collect_script_lines()
		self._write_script_file(file_name, script_lines)
		common.name_of_file_written_to = file_name
		self._display_saved_script(script_lines, file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _collect_script_lines(self) -> list[str]:
		"""Collect command lines from command history for script."""
		command_states = self._director.command_states
		command_exit_code = self._director.command_exit_code

		script_lines = []
		for i, cmd_state in enumerate(command_states):
			# Skip if command failed or still in process
			if command_exit_code[i] != 0:
				continue
			# Skip if no CommandState (command had no parameters)
			if cmd_state is None:
				continue
			# Build and add command line
			cmd_line = self._build_command_line(cmd_state)
			self._add_command_line_if_valid(cmd_line, script_lines)
		return script_lines

	# ------------------------------------------------------------------------

	def _build_command_line(self, cmd_state: object) -> str:
		"""Build command line with parameters from command state."""
		if not self._is_valid_command_for_script(cmd_state):
			return ""
		cmd_line = cmd_state.command_name
		cmd_line = self._add_parameters_to_command_line(
			cmd_line, cmd_state)
		return cmd_line

	# ------------------------------------------------------------------------

	def _is_valid_command_for_script(self, cmd_state: object) -> bool:
		"""Check if command should be included in script."""
		if not cmd_state.command_name:
			return False
		if cmd_state.command_type == "script":
			return False
		if cmd_state.command_type == "interactive_only": # noqa: SIM103
			return False
		return True

	# ------------------------------------------------------------------------

	def _add_parameters_to_command_line(
		self,
		cmd_line: str,
		cmd_state: object
	) -> str:
		"""Add formatted parameters to command line."""
		if not cmd_state.command_params:
			return cmd_line
		formatted_params = self.common.format_parameters_for_display(
			cmd_state.command_name, cmd_state.command_params)
		param_parts = self._format_parameter_parts(formatted_params)
		params_str = " ".join(param_parts)
		return f"{cmd_line} {params_str}"

	# ------------------------------------------------------------------------

	def _format_parameter_parts(
		self,
		formatted_params: dict[str, object]
	) -> list[str]:
		"""Format parameter parts as key=value strings."""
		param_parts = []
		for each_key, each_value in formatted_params.items():
			formatted_part = self._format_single_parameter(
				each_key, each_value)
			param_parts.append(formatted_part)
		return param_parts

	# ------------------------------------------------------------------------

	def _format_single_parameter(self, key: str, value: object) -> str:
		"""Format a single parameter as key=value string."""
		if isinstance(value, str):
			return f'{key}="{value}"'
		if isinstance(value, (list, dict)):
			return f'{key}={value}'
		return f'{key}={value}'

	# ------------------------------------------------------------------------

	def _add_command_line_if_valid(
		self,
		cmd_line: str,
		script_lines: list[str]
	) -> None:
		"""Add command line to script lines if valid."""
		if cmd_line:
			script_lines.append(cmd_line)
		return

	# ------------------------------------------------------------------------

	def _write_script_file(
		self,
		file_name: str,
		script_lines: list[str]
	) -> None:
		"""Write script lines to file."""
		try:
			self._write_file_with_header(file_name, script_lines)
		except (OSError, UnicodeEncodeError) as e:
			script_fail_title = "Save script failed"
			script_fail_message = f"Unable to write script file: {e}"
			raise SpacesError(script_fail_title, script_fail_message) from e
		self._director.common.script_lines = script_lines
		self._director.common.file_name = file_name
		return

	# ------------------------------------------------------------------------

	def _write_file_with_header(
		self,
		file_name: str,
		script_lines: list[str]
	) -> None:
		"""Write file with header and script lines."""
		with Path(file_name).open("w", encoding="utf-8") as f:
			self._write_header(f)
			self._write_script_lines(f, script_lines)
		return

	# ------------------------------------------------------------------------

	def _write_header(self, f: object) -> None:
		"""Write script header to file."""
		f.write("# Spaces Script\n")
		f.write(
			f"# Created: "
			f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n") # noqa: DTZ005
		f.write("# Spaces Version: 2025\n")
		return

	# ------------------------------------------------------------------------

	def _write_script_lines(self, f: object, script_lines: list[str]) -> None:
		"""Write script lines to file."""
		for each_index, each_line in enumerate(script_lines):
			self._write_single_line(f, each_line, each_index, script_lines)
		return

	# ------------------------------------------------------------------------

	def _write_single_line(
		self,
		f: object,
		line: str,
		index: int,
		script_lines: list[str]
	) -> None:
		"""Write a single line to file."""
		if index == len(script_lines) - 1:
			f.write(line)
		else:
			f.write(f"{line}\n")
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
		return

	# ------------------------------------------------------------------------


class SaveSimilaritiesCommand:
	"""The Save similarities command is used to write a copy of the active
	similarities to a file.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save similarities"
		self._save_similarities_error_title = "Similarities save problem"
		self._save_similarities_error_message = (
			"Unable to write similarities file.\n"
			"Check file path and permissions, then try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save similarities")
		file_name: str = params["file"]
		common.capture_and_push_undo_state(
			"Save similarities", "passive", params
		)
		self._write_similarities_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_save_similarities_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_similarities_file(self, file_name: str) -> None:
		"""Write similarities to lower triangular file with error handling."""
		try:
			self.common.write_lower_triangle(
				file_name,
				self._director.similarities_active.similarities_as_list,
				self._director.similarities_active.nitem,
				self._director.similarities_active.item_labels,
				self._director.similarities_active.item_names,
				8,
				5,
			)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_similarities_error_title,
				self._save_similarities_error_message,
			) from e

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

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Save target"
		self._save_target_error_title = "Target save problem"
		self._save_target_error_message = (
			"Unable to write target file.\n"
			"Check file path and permissions, then try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Save target")
		file_name: str = params["file"]
		common.capture_and_push_undo_state("Save target", "passive", params)
		self._write_target_file(file_name)
		common.name_of_file_written_to = file_name
		self._print_active_target_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _write_target_file(self, file_name: str) -> None:
		"""Write target to file with error handling."""
		try:
			self._director.common.write_configuration_type_file(
				file_name, self._director.target_active)
		except (OSError, PermissionError, ValueError) as e:
			raise SpacesError(
				self._save_target_error_title,
				self._save_target_error_message,
			) from e

	# ------------------------------------------------------------------------

	def _print_active_target_confirmation(self, file_name: str) -> None:
		print(
			f"\n\tThe active target has been written to:\n\t{file_name}\n"
		)
		return


# ----------------------------------------------------------------------------


class SettingsDisplayCommand:
	"""The Settings display sizing command sets display options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - display sizing"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters(
			"Settings - display sizing")
		axis_extra: int = params["axis_extra"]
		displacement: int = params["displacement"]
		point_size: int = params["point_size"]
		common.capture_and_push_undo_state(
			"Settings - display sizing", "active", params)

		# Apply settings - convert percentages to floats
		common.axis_extra = axis_extra / 100.0
		common.displacement = displacement / 100.0
		common.point_size = point_size

		common.print_display_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for display sizing settings confirmation.

		Returns:
			QTextEdit widget showing updated display sizing settings
		"""

		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(150)
		settings_text = (
			f"Axis extra margin: {self.common.axis_extra * 100:.1f}%\n"
			f"Label displacement: {self.common.displacement * 100:.1f}%\n"
			f"Point size: {self.common.point_size}"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SettingsLayoutCommand:
	"""The Settings layout options command is used to set layout options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - layout options"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters(
			"Settings - layout options")
		max_cols: int = params["max_cols"]
		width: int = params["width"]
		decimals: int = params["decimals"]
		common.capture_and_push_undo_state(
			"Settings - layout options", "active", params)

		# Apply settings
		common.max_cols = max_cols
		common.width = width
		common.decimals = decimals

		common.print_layout_options_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for layout options confirmation.

		Returns:
			QTextEdit widget showing updated layout options
		"""

		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(150)
		settings_text = (
			f"Maximum columns: {self.common.max_cols}\n"
			f"Column width: {self.common.width}\n"
			f"Decimal places: {self.common.decimals}"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SettingsPlaneCommand:
	"""The Settings plane command is used to set the viewing plane."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - plane"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Settings - plane")
		horizontal: str = params["horizontal"]
		vertical: str = params["vertical"]
		(hor_dim, vert_dim) = \
			self.detect_acceptability_of_plane_parameters(horizontal, vertical)
		common.capture_and_push_undo_state(
			"Settings - plane", "active", params)

		# Apply settings
		common.hor_dim = hor_dim
		common.vert_dim = vert_dim
		self._director.configuration_active.hor_axis_name = horizontal
		self._director.configuration_active.vert_axis_name = vertical

		common.print_plane_settings()
		common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for plane settings confirmation.

		Returns:
			QTextEdit widget showing updated plane settings
		"""

		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(120)
		settings_text = (
			f"Horizontal axis: "
			f"{self._director.configuration_active.hor_axis_name}\n"
			f"Vertical axis: "
			f"{self._director.configuration_active.vert_axis_name}"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------

	def detect_acceptability_of_plane_parameters(
		self, horizontal: str, vertical: str) -> tuple[int, int]:
		"""Detect if plane parameters are acceptable."""
		hor_dim: int | None = None
		vert_dim: int | None = None
		dim_names = self._director.configuration_active.dim_names

		if not horizontal or not vertical:
			missing_parameter_title = "Missing plane parameter"
			missing_parameter_message = (
				"Both horizontal and vertical parameters must be provided")
			raise SpacesError(
				missing_parameter_title, missing_parameter_message)

		try:
			hor_dim = dim_names.index(horizontal)
			vert_dim = dim_names.index(vertical)
		except ValueError as e:
			invalid_dimension_title = "Invalid dimension name"
			invalid_dimension_message = (
				f"Dimension names must be from {dim_names}, "
				f"got horizontal='{horizontal}', vertical='{vertical}'"
			)
			raise SpacesError(invalid_dimension_title,
				invalid_dimension_message,
			) from e

		# Validate that horizontal and vertical are different
		if hor_dim == vert_dim:
			invalid_plane_title = "Invalid plane parameters"
			invalid_plane_message = (
				"Horizontal and vertical axes must be different dimensions")
			raise SpacesError(invalid_plane_title, invalid_plane_message)
		return (hor_dim, vert_dim)

#----------------------------------------------------------------------------


class SettingsPlotCommand:
	"""The Settings plot settings command is used to set plot settings."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - plot settings"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Settings - plot settings")
		bisector: bool = params["bisector"]
		connector: bool = params["connector"]
		reference_points: bool = params["reference_points"]
		just_reference_points: bool = params["just_reference_points"]
		common.capture_and_push_undo_state(
			"Settings - plot settings", "active", params)

		# Apply settings
		common.show_bisector = bisector
		common.show_connector = connector
		common.show_reference_points = reference_points
		common.show_just_reference_points = just_reference_points

		common.print_plot_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for plot settings confirmation.

		Returns:
			QTextEdit widget showing updated plot settings
		"""
		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(150)
		settings_text = (
			f"Show bisector if available: "
			f"{self.common.show_bisector}\n"
			f"Show connector if available: "
			f"{self.common.show_connector}\n"
			f"Show reference points if available: "
			f"{self.common.show_reference_points}\n"
			f"In Joint plots show just reference points: "
			f"{self.common.show_just_reference_points}"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SettingsPresentationLayerCommand:
	"""The Settings presentation layer command sets the layer."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - presentation layer"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, layer: str | None = None) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters(
			"Settings - presentation layer", layer=layer)
		layer: str = params["layer"]
		common.capture_and_push_undo_state(
			"Settings - presentation layer", "active", params)

		# Apply presentation layer setting
		common.presentation_layer = layer

		common.print_presentation_layer_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for presentation layer confirmation.

		Returns:
			QTextEdit widget showing updated presentation layer setting
		"""
		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(100)
		settings_text = (
			f"Layer: {self._director.common.presentation_layer}")
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SettingsSegmentCommand:
	"""The Settings segment sizing command sets segment options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - segment sizing"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters(
			"Settings - segment sizing")
		battleground: int = params["battleground"]
		core: int = params["core"]
		common.capture_and_push_undo_state(
			"Settings - segment sizing", "active", params)

		# Apply settings (convert from 0-100 to 0.0-1.0)
		common.battleground_size = battleground / 100.0
		common.core_tolerance = core / 100.0

		common.print_segment_sizing_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for segment sizing settings confirmation.

		Returns:
			QTextEdit widget showing updated segment sizing settings
		"""

		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(120)
		settings_text = (
			f"Battleground size: {self.common.battleground_size * 100:.0f}%\n"
			f"Core tolerance: {self.common.core_tolerance * 100:.0f}%"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SettingsVectorSizeCommand:
	"""The Settings vector sizing command sets vector options."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - vector sizing"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Settings - vector sizing")
		vector_head_width: float = params["vector_head_width"]
		vector_width: float = params["vector_width"]
		common.capture_and_push_undo_state(
			"Settings - vector sizing", "active", params)

		# Apply settings
		common.vector_head_width = vector_head_width
		common.vector_width = vector_width

		common.print_vector_sizing_settings()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> object:
		"""Display widget for vector sizing settings confirmation.

		Returns:
			QTextEdit widget showing updated vector sizing settings
		"""

		widget = QTextEdit()
		widget.setReadOnly(True)
		widget.setMinimumHeight(120)
		settings_text = (
			f"Vector head width (in inches): {self.common.vector_head_width}\n"
			f"Vector width (in inches): {self.common.vector_width}"
		)
		widget.setPlainText(settings_text)
		return widget

	# ------------------------------------------------------------------------


class SimilaritiesCommand:
	"""The Similarities command is used to read a similarities file."""

	def __init__(self, director: Status, common: Spaces) -> None: # noqa: ARG002
		self._director = director
		self._director.command = "Similarities"
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
		common.initiate_command_processes()
		params = common.get_command_parameters(
			"Similarities", value_type=value_type)
		file_name: str = params["file"]
		value_type: str = params["value_type"]
		common.capture_and_push_undo_state(
			"Similarities", "active", params)
		self._read_similarities(file_name, value_type, common)
		self._director.dependency_checker.detect_consistency_issues()
		width = 8
		decimals = 3
		self._director.similarities_active.print_the_similarities(
			width, decimals, common)
		common.create_plot_for_tabs("heatmap_simi")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_similarities(
		self, file_name: str, value_type: str, common: Spaces
	) -> None:
		"""Read similarities from lower triangular file and store in active.

		Similarities are stored in a lower triangular matrix format and can
		be either "similarities" or "dissimilarities" based on value_type.
		"""
		try:
			self._director.similarities_active = (
				common.read_lower_triangular_matrix(file_name, value_type)
			)
			self._director.similarities_active.duplicate_similarities(common)
			self._director.similarities_active.range_similarities = \
				range(len(
					self._director.similarities_active.similarities_as_list))
			self._director.similarities_active.rank_similarities()
			common.rank_when_similarities_match_configuration()
		except (
			FileNotFoundError,
			PermissionError,
			ValueError,
			SpacesError
		):
			restored = common.event_driven_optional_restoration(
				"similarities"
			)
			# Only raise exception if restoration failed
			# If restored, just return - restoration message already
			# informed user
			if not restored:
				restore_title =self._similarities_error_bad_input_title
				restore_message = self._similarities_error_bad_input_message
				raise SpacesError(
					restore_title, restore_message) from None

			# If restored successfully, just return without error
			return

	# ------------------------------------------------------------------------


class TargetCommand:
	"""The Target command is used to open a target file."""

	def __init__(self, director: Status, common: Spaces) -> None: # noqa: ARG002
		self._director = director
		self._director.command = "Target"
		self._target_error_bad_input_title = "Target problem"
		self._target_error_bad_input_message = (
			"Input is inconsistent with a target file.\nLook at the "
			"contents of file and try again."
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Target")
		file_name: str = params["file"]
		common.capture_and_push_undo_state("Target", "active", params)

		# Read and validate target file
		self._director.target_active = common.read_configuration_type_file(
			file_name, "Target")
		self._director.dependency_checker.detect_consistency_issues()

		self._director.target_active.print_target()
		common.create_plot_for_tabs("target")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return
