from __future__ import annotations

import pandas as pd
import peek  # noqa: F401
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from typing import TYPE_CHECKING

from command_state import CommandState
from exceptions import SpacesError

if TYPE_CHECKING:
	from common import Spaces
	from director import Status


# ------------------------------------------------------------------------


class RedoCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Redo"

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Redo")
		common.capture_and_push_undo_state("Redo", "active", params)
		self._redo_last_undone_command()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _redo_last_undone_command(self) -> None:
		"""Restore state from the most recent CommandState on redo stack."""
		cmd_state = self._director.pop_redo_state()

		if cmd_state is None:
			title_msg: str = "Nothing to redo"
			detail_msg: str = (
				"No commands have been undone. "
				"Use Undo before using Redo."
			)
			raise SpacesError(title_msg, detail_msg)

		# Skip Undo/Redo meta-commands - only redo actual commands
		# But preserve them in undo stack so they appear in saved scripts
		if cmd_state.command_name in ("Undo", "Redo"):
			self._director.push_undo_state(cmd_state, preserve_redo_stack=True)
			return self._redo_last_undone_command()

		# Skip passive and script commands - only active commands have state to restore
		# But preserve them in undo stack so they appear in saved scripts
		if cmd_state.command_type in ("passive", "script"):
			self._director.push_undo_state(cmd_state, preserve_redo_stack=True)
			return self._redo_last_undone_command()

		print(f"\n\tRedoing {cmd_state.command_name} command")

		# Push the current state to undo stack before redoing
		current_state = CommandState(
			cmd_state.command_name, "active", cmd_state.command_params
		)
		current_state.timestamp = cmd_state.timestamp
		# Capture all state types that were in the original command
		for feature_name in cmd_state.state_snapshot:
			capture_method = getattr(
				current_state, f"capture_{feature_name}_state", None
			)
			if capture_method:
				capture_method(self._director)
		self._director.push_undo_state(current_state, preserve_redo_stack=True)

		# Restore all captured state
		cmd_state.restore_all_state(self._director)

		# After restoring the active command, continue restoring any passive
		# commands that were skipped over during the original undo
		while self._director.redo_stack:
			next_cmd = self._director.peek_redo_state()
			if next_cmd and next_cmd.command_type in ("passive", "script"):
				passive_cmd = self._director.pop_redo_state()
				self._director.push_undo_state(passive_cmd, preserve_redo_stack=True)
			else:
				break

		# Enable Undo now that undo stack has an item
		self._director.enable_undo()

		# Disable Redo if the redo stack is now empty
		if not self._director.redo_stack:
			self._director.disable_redo()

		# Build appropriate output and title based on restored state
		self._build_redo_output(cmd_state)

		return None

	# ------------------------------------------------------------------------

	def _build_redo_output(self, cmd_state: CommandState) -> None:
		"""Build output and title based on what was redone."""
		# Store the redone command name for title generator to access
		self.common.redone_command_name = cmd_state.command_name

		# Store the command state for _display() to use
		self._restored_cmd_state = cmd_state

		# If configuration was restored, recreate the plot
		if self._director.common.have_active_configuration():
			self._director.configuration_active.print_active_function()
			self._director.common.create_plot_for_tabs("configuration")

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create and return the table widget for the redo output.

		This method is called by the widget system after execute()
		completes to build the output display.
		"""
		# Build and return restoration details table
		table_widget = self._build_restoration_table(self._restored_cmd_state)
		self._director.output_widget_type: str = "Table"
		return table_widget

	# ------------------------------------------------------------------------

	def _build_restoration_table(
		self, cmd_state: CommandState
	) -> QTableWidget:
		"""Build and return a table widget showing what was restored.

		Args:
			cmd_state: The CommandState containing restoration details

		Returns:
			QTableWidget displaying the restoration details
		"""
		# Extract restoration details from cmd_state
		restoration_data = self._extract_restoration_details(cmd_state)

		if not restoration_data:
			# No items were restored, create empty table widget
			table_widget: QTableWidget = QTableWidget(1, 1)
			table_widget.setItem(
				0, 0, QTableWidgetItem("No state items were restored")
			)
			return table_widget

		# Create DataFrame for the table
		columns: list[str] = ["Items Restored", "Details"]
		df: pd.DataFrame = pd.DataFrame(restoration_data, columns=columns)

		# Create table widget
		table_widget: QTableWidget = QTableWidget(df.shape[0], df.shape[1])
		# Fill table with data
		self._director.common.fill_table_with_formatted_data(
			table_widget, df, ["s", "s"]  # Both columns are strings
		)

		# Set headers
		self._director.common.set_column_and_row_headers(
			table_widget, ["Items Restored", "Details"], []
		)

		# Resize and finalize
		self._director.common.resize_and_set_table_size(table_widget, 4)

		return table_widget

	# ------------------------------------------------------------------------

	def _extract_restoration_details(
		self, cmd_state: CommandState
	) -> list[list[str]]:
		"""Extract details about what was restored from current state.

		Args:
			cmd_state: The CommandState indicating what types were restored

		Returns:
			List of [item_name, details] pairs showing current state
		"""
		restoration_details: list[list[str]] = []
		# Get list of what was restored from the snapshot keys
		restored_types = cmd_state.state_snapshot.keys()

		# Use the same helper methods from UndoCommand
		# We can create a temporary UndoCommand instance to reuse methods
		temp_undo = UndoCommand(self._director, self.common)
		temp_undo._add_current_config_details(
			restored_types, restoration_details
		)
		temp_undo._add_current_target_details(
			restored_types, restoration_details
		)
		temp_undo._add_current_distance_details(
			restored_types, restoration_details
		)
		temp_undo._add_current_data_details(
			restored_types, restoration_details
		)
		temp_undo._add_current_settings_details(
			restored_types, restoration_details, cmd_state
		)
		temp_undo._add_current_rivalry_details(
			restored_types, restoration_details
		)

		return restoration_details

	# ------------------------------------------------------------------------


class UndoCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Undo"

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Undo")
		self._undo_last_command()
		common.capture_and_push_undo_state("Undo", "active", params)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _undo_last_command(self) -> None:
		"""Restore state from the most recent CommandState on the stack."""
		cmd_state = self._director.pop_undo_state()

		if cmd_state is None:
			title_msg: str = "Nothing to undo"
			detail_msg: str = (
				"No commands have been executed yet. "
				"Execute an active command before using Undo."
			)
			raise SpacesError(title_msg, detail_msg)

		# Skip Undo/Redo meta-commands - only undo actual commands
		# But preserve them in redo stack so they appear in saved scripts
		if cmd_state.command_name in ("Undo", "Redo"):
			self._director.push_redo_state(cmd_state)
			return self._undo_last_command()

		# Skip passive and script commands - only active commands have state to restore
		# But preserve them in redo stack so they appear in saved scripts
		if cmd_state.command_type in ("passive", "script"):
			self._director.push_redo_state(cmd_state)
			return self._undo_last_command()

		print(f"\n\tUndoing {cmd_state.command_name} command")

		# Push the current state to redo stack before undoing
		# We need to capture the current state first
		current_state = CommandState(
			cmd_state.command_name, "active", cmd_state.command_params
		)
		current_state.timestamp = cmd_state.timestamp
		# Capture all state types that were in the original command
		for feature_name in cmd_state.state_snapshot:
			capture_method = getattr(
				current_state, f"capture_{feature_name}_state", None
			)
			if capture_method:
				capture_method(self._director)
		self._director.push_redo_state(current_state)

		# Enable Redo now that redo stack has an item
		self._director.enable_redo()

		# Disable Undo if the undo stack is now empty
		if not self._director.undo_stack:
			self._director.disable_undo()

		# Restore all captured state
		cmd_state.restore_all_state(self._director)

		# Build appropriate output and title based on restored state
		self._build_undo_output(cmd_state)

		return None

	# ------------------------------------------------------------------------

	def _build_undo_output(self, cmd_state: CommandState) -> None:
		"""Build output and title based on what was undone."""
		# Store the undone command name for title generator to access
		self.common.undone_command_name = cmd_state.command_name

		# Store the command state for _display() to use
		self._restored_cmd_state = cmd_state

		# If configuration was restored, recreate the plot
		if self._director.common.have_active_configuration():
			self._director.configuration_active.print_active_function()
			self._director.common.create_plot_for_tabs("configuration")

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create and return the table widget for the undo output.

		This method is called by the widget system after execute()
		completes to build the output display.
		"""
		# Build and return restoration details table
		table_widget = self._build_restoration_table(self._restored_cmd_state)
		self._director.output_widget_type: str = "Table"
		return table_widget

	# ------------------------------------------------------------------------

	def _build_restoration_table(
		self, cmd_state: CommandState
	) -> QTableWidget:
		"""Build and return a table widget showing what was restored.

		Args:
			cmd_state: The CommandState containing restoration details

		Returns:
			QTableWidget displaying the restoration details
		"""
		# Extract restoration details from cmd_state
		restoration_data = self._extract_restoration_details(cmd_state)

		if not restoration_data:
			# No items were restored, create empty table widget
			table_widget: QTableWidget = QTableWidget(1, 1)
			table_widget.setItem(
				0, 0, QTableWidgetItem("No state items were restored")
			)
			return table_widget

		# Create DataFrame for the table
		columns: list[str] = ["Items Restored", "Details"]
		df: pd.DataFrame = pd.DataFrame(restoration_data, columns=columns)

		# Create table widget
		table_widget: QTableWidget = QTableWidget(df.shape[0], df.shape[1])
		# Fill table with data
		self._director.common.fill_table_with_formatted_data(
			table_widget, df, ["s", "s"]  # Both columns are strings
		)

		# Set headers
		self._director.common.set_column_and_row_headers(
			table_widget, ["Items Restored", "Details"], []
		)

		# Resize and finalize
		self._director.common.resize_and_set_table_size(table_widget, 4)

		return table_widget

	# ------------------------------------------------------------------------

	def _extract_restoration_details(
		self, cmd_state: CommandState
	) -> list[list[str]]:
		"""Extract details about what was restored from current state.

		Args:
			cmd_state: The CommandState indicating what types were restored

		Returns:
			List of [item_name, details] pairs showing current state
		"""
		restoration_details: list[list[str]] = []
		# Get list of what was restored from the snapshot keys
		restored_types = cmd_state.state_snapshot.keys()

		# Report on current state for each restored type
		self._add_current_config_details(restored_types, restoration_details)
		self._add_current_target_details(restored_types, restoration_details)
		self._add_current_distance_details(restored_types, restoration_details)
		self._add_current_data_details(restored_types, restoration_details)
		self._add_current_settings_details(
			restored_types, restoration_details, cmd_state
		)
		self._add_current_rivalry_details(restored_types, restoration_details)

		return restoration_details

	# ------------------------------------------------------------------------

	def _add_current_config_details(
		self, restored_types: list, details: list[list[str]]
	) -> None:
		"""Add current configuration details to restoration list."""
		if "configuration" in restored_types:
			config = self._director.configuration_active
			ndim: int = config.ndim
			npoint: int = config.npoint
			# Show coordinates info - this is what most commands modify
			point_coords = config.point_coords
			if point_coords is not None and not point_coords.empty:
				coords_text: str = f"{ndim} dimensions, {npoint} points"
				details.append(["Coordinates", coords_text])
			# Only show metadata if dimensions actually changed
			details.append(
				["Configuration", f"{ndim} dimensions, {npoint} points"])

	# ------------------------------------------------------------------------

	def _add_current_target_details(
		self, restored_types: list, details: list[list[str]]
	) -> None:
		"""Add current target details to restoration list."""
		if "target" in restored_types:
			target = self._director.target_active
			ndim: int = target.ndim
			npoint: int = target.npoint
			details.append(["Target", f"{ndim} dimensions, {npoint} points"])

	# ------------------------------------------------------------------------

	def _add_current_distance_details(
		self, restored_types: list, details: list[list[str]]
	) -> None:
		"""Add current distance matrix details to restoration list."""
		if "configuration" in restored_types:
			config = self._director.configuration_active
			dist_df: pd.DataFrame = config.distances_as_dataframe
			if dist_df is not None and not dist_df.empty:
				nrows, ncols = dist_df.shape
				details.append(["Distances", f"{nrows}x{ncols} matrix"])

	# ------------------------------------------------------------------------

	def _add_current_data_details(
		self, restored_types: list, details: list[list[str]]
	) -> None:
		"""Add current data-related details."""
		if "correlations" in restored_types:
			corr = self._director.correlations_active
			nitem: int = corr.nitem
			details.append(["Correlations", f"{nitem} items"])

		if "individuals" in restored_types:
			inds = self._director.individuals_active
			n_individ: int = inds.n_individ
			nvar: int = inds.nvar
			details.append(
				["Individuals", f"{n_individ} individuals, {nvar} variables"]
			)

		if "similarities" in restored_types:
			sims = self._director.similarities_active
			nitem: int = sims.nitem
			value_type: str = sims.value_type
			details.append(["Similarities", f"{nitem} items, {value_type}"])

		if "evaluations" in restored_types:
			evals = self._director.evaluations_active
			nitem: int = evals.nitem
			nevaluators: int = evals.nevaluators
			text: str = f"{nitem} items, {nevaluators} evaluators"
			details.append(["Evaluations", text])

		if "scores" in restored_types:
			scores = self._director.scores_active
			nscored_individ: int = scores.nscored_individ
			ndim: int = scores.ndim
			text: str = f"{ndim} dimensions, {nscored_individ} individuals"
			details.append(["Scores", text])

		if "grouped_data" in restored_types:
			grouped = self._director.grouped_data_active
			ngroups: int = grouped.ngroups
			ndim: int = grouped.ndim
			grouping_var: str = grouped.grouping_var
			text: str = \
				f"{ndim} dimensions, {ngroups} groups, var={grouping_var}"
			details.append(["Grouped data", text])

		if "uncertainty" in restored_types:
			unc = self._director.uncertainty_active
			nsolutions: int = unc.nsolutions
			npoints: int = unc.npoints
			details.append(
				["Uncertainty", f"{nsolutions} solutions, {npoints} points"]
			)

	# ------------------------------------------------------------------------

	def _add_current_settings_details(
		self,
		restored_types: list,
		details: list[list[str]],
		cmd_state: CommandState,
	) -> None:
		"""Add current settings details to restoration list.

		Shows only the settings relevant to the specific Settings command
		that was executed.

		Args:
			restored_types: List of state types that were restored
			details: List to append restoration details to
			cmd_state: CommandState containing command_name to determine
				which settings to show
		"""
		if "settings" not in restored_types:
			return

		common = self._director.common
		command_name: str = cmd_state.command_name

		# Settings - plane: Show horizontal and vertical dimensions
		if command_name == "Settings - plane":
			self._add_plane_details(common, details)

		# Settings - presentation layer: Show layer
		elif command_name == "Settings - presentation layer":
			layer: str = common.presentation_layer
			details.append(["layer", layer])

		# Settings - plot settings: Show plot display options
		elif command_name == "Settings - plot settings":
			self._add_plot_settings_details(common, details)

		# Settings - display sizing: Show sizing parameters
		elif command_name == "Settings - display sizing":
			self._add_display_sizing_details(common, details)

		# Settings - vector sizing: Show vector parameters
		elif command_name == "Settings - vector sizing":
			self._add_vector_sizing_details(common, details)

		# Settings - segment sizing: Show segment parameters
		elif command_name == "Settings - segment sizing":
			self._add_segment_sizing_details(common, details)

		# Settings - layout options: Show layout parameters
		elif command_name == "Settings - layout options":
			self._add_layout_options_details(common, details)

	# ------------------------------------------------------------------------

	def _add_plane_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add plane (horizontal/vertical dimension) details."""
		hor_dim: int = common.hor_dim
		vert_dim: int = common.vert_dim

		# Get dimension names if configuration is available
		hor_name: str = f"dim {hor_dim}"
		vert_name: str = f"dim {vert_dim}"
		if common.have_active_configuration():
			config = self._director.configuration_active
			if 0 <= hor_dim < len(config.dim_names):
				hor_name = f'"{config.dim_names[hor_dim]}"'
			if 0 <= vert_dim < len(config.dim_names):
				vert_name = f'"{config.dim_names[vert_dim]}"'

		details.append(["horizontal", hor_name])
		details.append(["vertical", vert_name])

	# ------------------------------------------------------------------------

	def _add_plot_settings_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add plot settings details."""
		details.append(["bisector", str(common.show_bisector)])
		details.append(["connector", str(common.show_connector)])
		details.append(["reference_points", str(common.show_reference_points)])
		details.append(
			["just_reference_points", str(common.show_just_reference_points)]
		)

	# ------------------------------------------------------------------------

	def _add_display_sizing_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add display sizing details."""
		details.append(["axis_extra", str(common.axis_extra)])
		details.append(["displacement", str(common.displacement)])
		details.append(["point_size", str(common.point_size)])

	# ------------------------------------------------------------------------

	def _add_vector_sizing_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add vector sizing details."""
		details.append(["vector_head_width", str(common.vector_head_width)])
		details.append(["vector_width", str(common.vector_width)])

	# ------------------------------------------------------------------------

	def _add_segment_sizing_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add segment sizing details."""
		details.append(
			["battleground_size", str(common.battleground_size * 100)]
		)
		details.append(["core_tolerance", str(common.core_tolerance * 100)])

	# ------------------------------------------------------------------------

	def _add_layout_options_details(
		self, common: Spaces, details: list[list[str]]
	) -> None:
		"""Add layout options details."""
		details.append(["max_cols", str(common.max_cols)])
		details.append(["width", str(common.width)])
		details.append(["decimals", str(common.decimals)])

	# ------------------------------------------------------------------------

	def _add_current_rivalry_details(
		self, restored_types: list, details: list[list[str]]
	) -> None:
		"""Add current rivalry details to restoration list."""
		if "rivalry" in restored_types:
			riv = self._director.rivalry
			rival_a_name: str = (
				riv.rival_a.name if riv.rival_a.name else "unknown"
			)
			rival_b_name: str = (
				riv.rival_b.name if riv.rival_b.name else "unknown"
			)
			details.append(
				["Reference points", f"{rival_a_name} vs {rival_b_name}"]
			)

			# Check if segments were restored
			if riv.seg is not None and not riv.seg.empty:
				nsegments: int = len(riv.seg)
				details.append(["Segments", f"{nsegments} segments restored"])

			# Check if bisector and other lines were restored
			lines_restored = [
				line_name
				for line_name in [
					"bisector", "east", "west", "connector", "first", "second"
				]
				if getattr(riv, line_name, None) is not None
			]
			if lines_restored:
				line_list: str = ", ".join(lines_restored)
				details.append(["Lines", f"{line_list}"])

			# Check if percentages were restored
			pct_types: list[str] = []
			for pct_type in [
				"base_pcts",
				"battleground_pcts",
				"core_pcts",
				"likely_pcts"
			]:
				pcts = getattr(riv, pct_type, None)
				if pcts is not None and len(pcts) > 0:
					pct_types.append(pct_type.replace("_pcts", ""))
			if pct_types:
				pct_list: str = ", ".join(pct_types)
				details.append(["Percentages", f"{pct_list} restored"])
