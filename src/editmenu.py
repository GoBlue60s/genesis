from __future__ import annotations

import pandas as pd
import peek  # noqa: F401
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from typing import TYPE_CHECKING

from exceptions import SpacesError

if TYPE_CHECKING:
	from common import Spaces
	from director import Status
	from command_state import CommandState


# ------------------------------------------------------------------------


class RedoCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Redo"

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
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
			title_msg = "Nothing to redo"
			detail_msg = (
				"No commands have been undone. "
				"Use Undo before using Redo."
			)
			raise SpacesError(title_msg, detail_msg)

		print(f"\n\tRedoing {cmd_state.command_name} command")

		# Push the current state to undo stack before redoing
		from command_state import CommandState
		current_state = CommandState(cmd_state.command_name, "active", {})
		current_state.timestamp = cmd_state.timestamp
		# Capture all state types that were in the original command
		for feature_name in cmd_state.state_snapshot.keys():
			capture_method = getattr(
				current_state, f"capture_{feature_name}_state", None
			)
			if capture_method:
				capture_method(self._director)
		self._director.push_undo_state(current_state)

		# Restore all captured state
		cmd_state.restore_all_state(self._director)

		# Build appropriate output and title based on restored state
		self._build_redo_output(cmd_state)

		return

	# ------------------------------------------------------------------------

	def _build_redo_output(self, cmd_state: CommandState) -> None:
		"""Build output and title based on what was redone."""
		# Set simple title indicating what was redone
		self._director.title_for_table_widget = (
			f"Redid {cmd_state.command_name} command"
		)

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
		self._director.output_widget_type = "Table"
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
			table_widget = QTableWidget(1, 1)
			table_widget.setItem(
				0, 0, QTableWidgetItem("No state items were restored")
			)
			return table_widget

		# Create DataFrame for the table
		columns = ["Items Restored", "Details"]
		df = pd.DataFrame(restoration_data, columns=columns)

		# Create table widget
		table_widget = QTableWidget(df.shape[0], df.shape[1])

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
		"""Extract details about what was restored from CommandState.

		Args:
			cmd_state: The CommandState with state_snapshot

		Returns:
			List of [item_name, details] pairs for each restored item
		"""
		restoration_details = []
		snapshot = cmd_state.state_snapshot

		# Use the same helper methods from UndoCommand
		# We can create a temporary UndoCommand instance to reuse methods
		temp_undo = UndoCommand(self._director, self.common)
		temp_undo._add_config_details(snapshot, restoration_details)
		temp_undo._add_target_details(snapshot, restoration_details)
		temp_undo._add_distance_details(snapshot, restoration_details)
		temp_undo._add_data_details(snapshot, restoration_details)
		temp_undo._add_settings_details(snapshot, restoration_details)
		temp_undo._add_rivalry_details(snapshot, restoration_details)

		return restoration_details

	# ------------------------------------------------------------------------


class UndoCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Undo"

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._undo_last_command()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _undo_last_command(self) -> None:
		"""Restore state from the most recent CommandState on the stack."""
		cmd_state = self._director.pop_undo_state()

		if cmd_state is None:
			title_msg = "Nothing to undo"
			detail_msg = (
				"No commands have been executed yet. "
				"Execute an active command before using Undo."
			)
			raise SpacesError(title_msg, detail_msg)

		print(f"\n\tUndoing {cmd_state.command_name} command")

		# Push the current state to redo stack before undoing
		# We need to capture the current state first
		from command_state import CommandState
		current_state = CommandState(cmd_state.command_name, "active", {})
		current_state.timestamp = cmd_state.timestamp
		# Capture all state types that were in the original command
		for feature_name in cmd_state.state_snapshot.keys():
			capture_method = getattr(
				current_state, f"capture_{feature_name}_state", None
			)
			if capture_method:
				capture_method(self._director)
		self._director.push_redo_state(current_state)

		# Enable Redo now that redo stack has an item
		self._director.enable_redo()

		# Restore all captured state
		cmd_state.restore_all_state(self._director)

		# Build appropriate output and title based on restored state
		self._build_undo_output(cmd_state)

		return

	# ------------------------------------------------------------------------

	def _build_undo_output(self, cmd_state: CommandState) -> None:
		"""Build output and title based on what was undone."""
		# Set simple title indicating what was undone
		self._director.title_for_table_widget = (
			f"Undid {cmd_state.command_name} command"
		)

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
		self._director.output_widget_type = "Table"
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
			table_widget = QTableWidget(1, 1)
			table_widget.setItem(
				0, 0, QTableWidgetItem("No state items were restored")
			)
			return table_widget

		# Create DataFrame for the table
		columns = ["Items Restored", "Details"]
		df = pd.DataFrame(restoration_data, columns=columns)

		# Create table widget
		table_widget = QTableWidget(df.shape[0], df.shape[1])

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
		"""Extract details about what was restored from CommandState.

		Args:
			cmd_state: The CommandState with state_snapshot

		Returns:
			List of [item_name, details] pairs for each restored item
		"""
		restoration_details = []
		snapshot = cmd_state.state_snapshot

		# Process each type of state item
		self._add_config_details(snapshot, restoration_details)
		self._add_target_details(snapshot, restoration_details)
		self._add_distance_details(snapshot, restoration_details)
		self._add_data_details(snapshot, restoration_details)
		self._add_settings_details(snapshot, restoration_details)
		self._add_rivalry_details(snapshot, restoration_details)

		return restoration_details

	# ------------------------------------------------------------------------

	def _add_config_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add configuration details to restoration list."""
		if "configuration" in snapshot:
			config = snapshot["configuration"]
			ndim = config.get("ndim", 0)
			npoint = config.get("npoint", 0)
			# Show coordinates info - this is what most commands modify
			point_coords = config.get("point_coords")
			if point_coords is not None and not point_coords.empty:
				coords_text = f"{ndim} dimensions, {npoint} points"
				details.append(["Coordinates", coords_text])
			# Only show metadata if dimensions actually changed
			details.append(["Configuration", f"{ndim} dimensions, {npoint} points"])

	# ------------------------------------------------------------------------

	def _add_target_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add target details to restoration list."""
		if "target" in snapshot:
			target = snapshot["target"]
			ndim = target.get("ndim", 0)
			npoint = target.get("npoint", 0)
			details.append(["Target", f"{ndim} dimensions, {npoint} points"])

	# ------------------------------------------------------------------------

	def _add_distance_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add distance matrix details to restoration list."""
		if "configuration" in snapshot:
			config = snapshot["configuration"]
			dist_df = config.get("distances_as_dataframe")
			if dist_df is not None and not dist_df.empty:
				nrows, ncols = dist_df.shape
				details.append(["Distances", f"{nrows}x{ncols} matrix"])

	# ------------------------------------------------------------------------

	def _add_data_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add data-related details (correlations, individuals, etc.)."""
		if "correlations" in snapshot:
			corr = snapshot["correlations"]
			nitem = corr.get("nitem", 0)
			details.append(["Correlations", f"{nitem} items"])

		if "individuals" in snapshot:
			inds = snapshot["individuals"]
			n_individ = inds.get("n_individ", 0)
			nvar = inds.get("nvar", 0)
			details.append(
				["Individuals", f"{n_individ} individuals, {nvar} variables"]
			)

		if "similarities" in snapshot:
			sims = snapshot["similarities"]["active"]
			nitem = sims.get("nitem", 0)
			value_type = sims.get("value_type", "unknown")
			details.append(["Similarities", f"{nitem} items, {value_type}"])

		if "evaluations" in snapshot:
			evals = snapshot["evaluations"]
			nitem = evals.get("nitem", 0)
			nevaluators = evals.get("nevaluators", 0)
			text = f"{nitem} items, {nevaluators} evaluators"
			details.append(["Evaluations", text])

		if "scores" in snapshot:
			scores = snapshot["scores"]
			nscored_individ = scores.get("nscored_individ", 0)
			ndim = scores.get("ndim", 0)
			text = f"{ndim} dimensions, {nscored_individ} individuals"
			details.append(["Scores", text])

		if "grouped_data" in snapshot:
			grouped = snapshot["grouped_data"]
			ngroups = grouped.get("ngroups", 0)
			ndim = grouped.get("ndim", 0)
			grouping_var = grouped.get("grouping_var", "unknown")
			text = f"{ndim} dimensions, {ngroups} groups, var={grouping_var}"
			details.append(["Grouped data", text])

		if "uncertainty" in snapshot:
			unc = snapshot["uncertainty"]
			nsolutions = unc.get("nsolutions", 0)
			npoints = unc.get("npoints", 0)
			details.append(
				["Uncertainty", f"{nsolutions} solutions, {npoints} points"]
			)

	# ------------------------------------------------------------------------

	def _add_settings_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add settings details to restoration list."""
		if "settings" in snapshot:
			settings = snapshot["settings"]
			hor_dim = settings.get("hor_dim", 0)
			vert_dim = settings.get("vert_dim", 0)
			layer = settings.get("presentation_layer", "unknown")
			text = f"hor_dim={hor_dim}, vert_dim={vert_dim}, layer={layer}"
			details.append(["Settings", text])

	# ------------------------------------------------------------------------

	def _add_rivalry_details(
		self, snapshot: dict, details: list[list[str]]
	) -> None:
		"""Add rivalry details to restoration list."""
		if "rivalry" in snapshot:
			riv = snapshot["rivalry"]
			rival_a_name = riv.get("rival_a_name", "unknown")
			rival_b_name = riv.get("rival_b_name", "unknown")
			details.append(
				["Reference points", f"{rival_a_name} vs {rival_b_name}"]
			)

			# Check if segments were restored
			seg = riv.get("seg")
			if seg is not None and not seg.empty:
				nsegments = len(seg)
				details.append(["Segments", f"{nsegments} segments restored"])

			# Check if bisector and other lines were restored
			lines_restored = [
				line_name
				for line_name in [
					"bisector", "east", "west", "connector", "first", "second"
				]
				if riv.get(line_name) is not None
			]
			if lines_restored:
				line_list = ", ".join(lines_restored)
				details.append(["Lines", f"{line_list}"])

			# Check if percentages were restored
			pct_types = []
			for pct_type in [
				"base_pcts",
				"battleground_pcts",
				"core_pcts",
				"likely_pcts"
			]:
				pcts = riv.get(pct_type)
				if pcts and len(pcts) > 0:
					pct_types.append(pct_type.replace("_pcts", ""))
			if pct_types:
				pct_list = ", ".join(pct_types)
				details.append(["Percentages", f"{pct_list} restored"])
