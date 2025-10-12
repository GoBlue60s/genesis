from __future__ import annotations

import peek  # noqa: F401
from typing import TYPE_CHECKING

from exceptions import SpacesError
from common import Spaces

if TYPE_CHECKING:
	from director import Status
	from command_state import CommandState


# ------------------------------------------------------------------------


class RedoCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Redo command has yet to be implemented."""
		self._director = director
		self.common = common
		self._director.command = "Redo"
		self._director.title_for_table_widget = (
			"Redo is under construction - stay tuned, please"
		)
		return

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()

		return

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

		# If configuration was restored, recreate the plot
		if self._director.common.have_active_configuration():
			self._director.configuration_active.print_active_function()
			self._director.common.create_plot_for_tabs("configuration")

		return
